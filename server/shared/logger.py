from django_redis import get_redis_connection
import logging


class RedisLoggingHandler(logging.Handler):
    def __init__(self, name="default", topic="default", nrecents=1000,
                 expiration=86400):
        self.redis = get_redis_connection(name)
        self.topic = topic
        self.nrecents = nrecents
        self.expiration = expiration

    def emit(self, record: logging.LogRecord):
        message = record.getMessage()
        with self.redis.pipeline() as pipe:
            pipe.lpush(self.topic, message)
            if self.nrecents:
                pipe.ltrim(self.topic, 0, self.nrecents)
            if self.expiration:
                pipe.expire(self.topic, self.expiration)
