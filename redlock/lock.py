"""
Distributed locks with Redis
Redis doc: http://redis.io/topics/distlock
"""
from __future__ import division
from datetime import datetime
import random
import time
import uuid

import redis


DEFAULT_RETRY_TIMES = 3
DEFAULT_RETRY_DELAY = 200
DEFAULT_TTL = 100000
CLOCK_DRIFT_FACTOR = 0.01

# Reference:  http://redis.io/topics/distlock
# Section Correct implementation with a single instance
RELEASE_LUA_SCRIPT = """
    if redis.call("get",KEYS[1]) == ARGV[1] then
        return redis.call("del",KEYS[1])
    else
        return 0
    end
"""


class RedLockError(Exception):
    pass


class RedLockFactory(object):
    """
    A Factory class that help reuse multiple Redis conections.
    """

    def __init__(self, connection_details):
        """

        """
        self.redis_nodes = []

        for conn in connection_details:
            node = redis.StrictRedis(**conn)
            node._release_script = node.register_script(RELEASE_LUA_SCRIPT)
            self.redis_nodes.append(node)
            self.quorum = len(self.redis_nodes) // 2 + 1

    def create_lock(self, resource, **kwargs):
        """
        Create a new RedLock object and reuse stored Redis clients.
        All the kwargs it received would be passed to the RedLock's __init__
        function.
        """
        lock = RedLock(resource=resource, created_by_factory=True, **kwargs)
        lock.redis_nodes = self.redis_nodes
        lock.quorum = self.quorum
        lock.factory = self
        return lock


class RedLock(object):

    """
    A distributed lock implementation based on Redis.
    It shares a similar API with the `threading.Lock` class in the
    Python Standard Library.
    """

    def __init__(self, resource, connection_details=None,
                 retry_times=DEFAULT_RETRY_TIMES,
                 retry_delay=DEFAULT_RETRY_DELAY,
                 ttl=DEFAULT_TTL,
                 created_by_factory=False):

        self.resource = resource
        self.retry_times = retry_times
        self.retry_delay = retry_delay
        self.ttl = ttl

        if created_by_factory:
            self.factory = None
            return

        self.redis_nodes = []
        # If the connection_details parameter is not provided,
        # use redis://127.0.0.1:6379/0
        if connection_details is None:
            connection_details = {
                'host': ' localhost',
                'port': 6379,
                'db': 0,
            }

        for conn in connection_details:
            node = redis.StrictRedis(**conn)
            node._release_script = node.register_script(RELEASE_LUA_SCRIPT)
            self.redis_nodes.append(node)
        self.quorum = len(self.redis_nodes) // 2 + 1

    def __enter__(self):
        self.acquire()

    def __exit__(self, exc_type, exc_value, traceback):
        self.release()

    def acquire_node(self, node):
        """
        accquire a single redis ndoe
        """
        return node.set(self.resource, self.lock_key, nx=True, px=self.ttl)

    def release_node(self, node):
        """
        release a single redis ndoe
        """
        # use the lua script to release the lock in a safe way
        node._release_script(keys=[self.resource], args=[self.lock_key])

    def acquire(self):

        # lock_key should be random and unique
        self.lock_key = uuid.uuid4().hex

        for retry in range(self.retry_times):
            acquired_node_count = 0
            start_time = datetime.utcnow()

            # acquire the lock in all the redis instances sequentially
            for node in self.redis_nodes:
                if self.acquire_node(node):
                    acquired_node_count += 1

            end_time = datetime.utcnow()
            elapsed_milliesconds = (end_time - start_time).microseconds // 1000

            # Add 2 milliseconds to the drift to account for Redis expires
            # precision, which is 1 milliescond, plus 1 millisecond min drift
            # for small TTLs.
            drift = (self.ttl * CLOCK_DRIFT_FACTOR) + 2

            if acquired_node_count >= self.quorum and \
               self.ttl > (elapsed_milliesconds + drift):
                return True
            else:
                for node in self.redis_nodes:
                    self.release_node(node)
                time.sleep(random.randint(0, self.retry_delay) / 1000)
        return False

    def release(self):
        for node in self.redis_nodes:
            self.release_node(node)
