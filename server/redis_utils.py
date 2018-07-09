import pickle


from django_redis import get_redis_connection


Redis = get_redis_connection()


def append_to_key_raw(k, *values, limit=1000):
    with Redis.pipeline() as p:
        p.lpush(k, *values)
        if limit:
            p.ltrim(k, 0, limit-1)
        return p.execute()


def append_to_key(k, *values, limit=1000):
    """Encode values using pickle and store them in the Redis cache. Newer messages
    will appear before older messages. Messages beyond the specified limit will
    be deleted.

    """
    return append_to_key_raw(k, *map(pickle.dumps, values), limit=limit)


def lget_key(k, limit=1000):
    return [pickle.loads(x) for x in Redis.lrange(k, 0, 1000)]


def set_key(k, v):
    Redis.get(k, pickle.dumps(v))


def get_key(k):
    v = Redis.get(k)
    return v and pickle.loads(v)


def set_many(kvs):
    with Redis.pipeline() as p:
        for k, v in kvs.items() if hasattr(kvs, "items") else kvs:
            p.set(k, pickle.dumps(v))
        p.execute()


def get_many(ks):
    with Redis.pipeline() as p:
        for k in ks:
            p.get(k)

        return [v and pickle.loads(v) for v in p.execute()]


def get_and_delete_key(k):
    with Redis.pipeline() as p:
        p.get(k)
        p.delete(k)
        [v, _] = p.execute()
    return v and pickle.loads(v)


def set_expire_key(k, v, ttl=86400):
    with Redis.pipeline() as p:
        p.set(k, pickle.dumps(v))
        p.expire(k, ttl)
        p.execute()
