import redis
from skyline.setting import configure
from skyline.setting import log

configure = configure.dal.driver.driver_redis


class Redis:
    def __init__(self, host: str=None, port: int=configure.port, password: str=None):
        self.__connection_pool = None
        self.__redis_handle = None
        self.__kwargs = {'host': host, 'port': port, 'password': password}
        self._default_connect()

    def __del__(self):
        self.close()

    def __getattr__(self, item):
        def null(*args, **kwargs):
            pass
        if self.__redis_handle is None:
            self._default_connect()
        if self.__redis_handle is not None:
            try:
                redis_method = getattr(self.__redis_handle, item)
                if redis_method is not None:
                    return self.guard(redis_method)
            except AttributeError:
                log.warning('Redis has no such method: {}'.format(item))
                return null
        else:
            log.warning('Redis has not connected')
            return null

    def guard(self, function):
        def _guard(*args, **kwargs):
            try:
                function_return = log.watch(function)(*args, **kwargs)
            except:
                self.close()
                function_return = None
            return function_return
        return _guard

    @log.guard
    def _default_connect(self):
        if self.__kwargs.get('host', None) is not None:
            self.connect(**self.__kwargs)

    @log.guard
    def connect(self, **kwargs: dict):
        self.__kwargs = kwargs
        try:
            self.__connection_pool = redis.ConnectionPool(**kwargs)
            self.__redis_handle = redis.Redis(connection_pool=self.__connection_pool)
            self.__redis_handle.client_getname()
        except redis.ConnectionError:
            log.exception()
            self.__connection_pool = None
            self.__redis_handle = None

    @log.guard
    def close(self):
        try:
            if self.__connection_pool is not None:
                self.__connection_pool.disconnect()
        finally:
            self.__connection_pool = None
            self.__redis_handle = None

    def restore(self):
        self._default_connect()

    def alive(self):
        return self.__redis_handle is not None
