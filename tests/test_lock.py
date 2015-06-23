from redlock import RedLock, RedLockError
import time


def test_default_connection_details_value():
    """
    Test that RedLock instance could be created with
    default value of `connection_details` argument.
    """
    lock = RedLock("test_simple_lock")


def test_simple_lock():
    """
    Test a RedLock can be acquired.
    """
    lock = RedLock("test_simple_lock", [{"host": "localhost"}], ttl=1000)
    locked = lock.acquire()
    lock.release()
    assert locked == True


def test_from_url():
    """
    Test a RedLock can be acquired via from_url.
    """
    lock = RedLock("test_from_url", [{"url": "redis://localhost/0"}], ttl=1000)
    locked = lock.acquire()
    lock.release()
    assert locked == True


def test_context_manager():
    """
    Test a RedLock can be released by the context manager automically.

    """
    with RedLock("test_context_manager", [{"host": "localhost"}], ttl=1000):
        lock = RedLock("test_context_manager", [{"host": "localhost"}], ttl=1000)
        locked = lock.acquire()
        assert locked == False

    lock = RedLock("test_context_manager", [{"host": "localhost"}], ttl=1000)
    locked = lock.acquire()
    assert locked == True

    # try to lock again within a with block
    try:
        with RedLock("test_context_manager", [{"host": "localhost"}]):
            # shouldn't be allowed since someone has the lock already
            assert False
    except RedLockError:
        # we expect this call to error out
        pass

    lock.release()


def test_fail_to_lock_acquired():
    lock1 = RedLock("test_fail_to_lock_acquired", [{"host": "localhost"}], ttl=1000)
    lock2 = RedLock("test_fail_to_lock_acquired", [{"host": "localhost"}], ttl=1000)

    lock1_locked = lock1.acquire()
    lock2_locked = lock2.acquire()
    lock1.release()

    assert lock1_locked == True
    assert lock2_locked == False


def test_lock_expire():
    lock1 = RedLock("test_lock_expire", [{"host": "localhost"}], ttl=500)
    lock1.acquire()
    time.sleep(1)

    # Now lock1 has expired, we can accquire a lock
    lock2 = RedLock("test_lock_expire", [{"host": "localhost"}], ttl=1000)
    locked = lock2.acquire()
    assert locked == True

    lock1.release()
    lock3 = RedLock("test_lock_expire", [{"host": "localhost"}], ttl=1000)
    locked = lock3.acquire()
    assert locked == False
