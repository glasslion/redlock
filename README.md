RedLock
=======

## RedLock - Distributed locks with Redis and Python

[![Build Status](https://travis-ci.org/glasslion/redlock.svg?branch=master)](https://travis-ci.org/glasslion/redlock)

This library implements the RedLock algorithm introduced by [@antirez](http://antirez.com/)

The detailed description of the RedLock algorithm can be found in the Redis documentation: [Distributed locks with Redis](http://redis.io/topics/distlock).


The `redlock.RedLock` class shares a similar API with the `threading.Lock` class in the  Python Standard Library.

### Simple Usage

```python
from redlock import RedLock
lock =  RedLock()
lock.acquire()
lock.release()
```

