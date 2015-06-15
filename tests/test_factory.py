from redlock import RedLockFactory


def test_factory_create():
    factory = RedLockFactory([{"host": "localhost"}])

    lock = factory.create_lock("test_factory_create", ttl=500, retry_times=5, retry_delay=100)

    assert factory.redis_nodes == lock.redis_nodes
    assert factory.quorum == lock.quorum
    assert lock.ttl == 500
    assert lock.retry_times == 5
    assert lock.retry_delay == 100
    assert lock.factory == factory


def test_factory_create_from_url():
    factory = RedLockFactory([{"url": "redis://localhost/0"}])

    lock = factory.create_lock(
        "test_factory_create_from_url", ttl=500, retry_times=5, retry_delay=100
    )

    assert factory.redis_nodes == lock.redis_nodes
    assert factory.quorum == lock.quorum
    assert lock.ttl == 500
    assert lock.retry_times == 5
    assert lock.retry_delay == 100
    assert lock.factory == factory
