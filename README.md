![RedLock logo](https://github.com/glasslion/redlock/raw/master/docs/assets/redlock-small.png)

## RedLock - Distributed locks with Redis and Python

[![Build Status](https://travis-ci.org/glasslion/redlock.svg?branch=master)](https://travis-ci.org/glasslion/redlock)

This library implements the RedLock algorithm introduced by [@antirez](http://antirez.com/)

The detailed description of the RedLock algorithm can be found in the Redis documentation: [Distributed locks with Redis](http://redis.io/topics/distlock).


The `redlock.RedLock` class shares a similar API with the `threading.Lock` class in the  Python Standard Library.

### Simple Usage

```python
from redlock import RedLock
lock =  RedLock("distributed_lock")
lock.acquire()
do_something()
lock.release()
```

### With Statement / Context Manager 

As with `threading.Lock`, `redlock.RedLock` objects are context managers thus support the [With Statement](https://docs.python.org/2/reference/datamodel.html#context-managers). Thsi way is more pythonic and recommended.

```python
from redlock import RedLock
with RedLock("distributed_lock"):
    do_something()
```

