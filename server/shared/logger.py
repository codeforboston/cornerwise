from django_redis import get_redis_connection
import logging


class RedisLoggingHandler(logging.Handler):
    def __init__(self, name="default", topic="default", nrecents=1000,
                 expiration=86400, **kwargs):
        super().__init__(**kwargs)
        self.redis = get_redis_connection(name)
        self.topic = topic
        self.nrecents = nrecents
        self.expiration = expiration

    def emit(self, record: logging.LogRecord):
        message = self.format(record)
        with self.redis.pipeline() as pipe:
            pipe.lpush(self.topic, message)
            if self.nrecents:
                pipe.ltrim(self.topic, 0, self.nrecents-1)
            if self.expiration:
                pipe.expire(self.topic, self.expiration)
            pipe.execute()
