from redlock import RedLock, RedLockFactory

def test_factory_create():
    factory = RedLockFactory([{"host": "localhost"}])

    lock = factory.create_lock(ttl=500, retry_times=5, retry_delay=100)

    assert factory.redis_nodes == lock.redis_nodes
    assert factory.quorum == lock.quorum
    assert lock.ttl == 500
    assert lock.retry_times == 5
    assert lock.ttl ==500
    assert lock.retry_delay == 100
    assert lock.factory == factory
