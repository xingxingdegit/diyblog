import redis
from config import REDIS
import logging

log = logging.getLogger(__name__)

class RedisGetConnect:
    pool = redis.ConnectionPool(
        host=REDIS['host'], port=REDIS['port'], 
        password=REDIS['password'], db=REDIS['db'], decode_responses=True)
    
    def __init__(self):
        self.__connect = redis.Redis(connection_pool=self.pool)

    def set(self, key, value, ex=None):
        return self.__connect.set(key, value, ex)

    def get(self, key):
        return self.__connect.get(key)

    def delete(self, key):
        return self.__connect.delete(key)

    def expire(self, key, second):
        return self.__connect.expire(key, second)

    def ttl(self, key):
        return self.__connect.ttl(key)

    def hmset(self, key, value):
        return self.__connect.hmset(key, value)

    def hset(self, key, hkey, hvalue):
        return self.__connect.hset(key, hkey, hvalue)

    def hgetall(self, key):
        return self.__connect.hgetall(key)

    def hget(self, key, hkey):
        return self.__connect.hget(key, hkey)

    def hkeys(self, key):
        return self.__connect.hkeys(key)

    def hdel(self, key, *hkeys):
        return self.__connect.hdel(key, *hkeys)
