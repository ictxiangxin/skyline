import redis
from skyline.setting import configure
from skyline.setting import log

configure = configure.dal.driver.driver_redis


class Redis:
    def __init__(self, host: str=None, port: int=None, password: str=None):
        self.__host = host
        self.__port = port
        self.__password = password
        self.__connection_pool = None
        self.__redis_handle = None
        self.__kwargs = {}
        self._default_connect()

    def __del__(self):
        if self.__connection_pool is not None:
            self.__connection_pool.disconnect()
            self.__connection_pool = None
            self.__redis_handle = None

    def __getattr__(self, item):
        def null(*args, **kwargs):
            pass
        if self.__redis_handle is None:
            self._default_connect()
        if self.__redis_handle is not None:
            redis_method = getattr(self.__redis_handle, item)
            if redis_method is not None:
                return log.guard(redis_method)
        else:
            return null

    def _default_connect(self):
        default_connect_arguments = {}
        if self.__host is not None:
            default_connect_arguments['host'] = self.__host
        if self.__port is not None:
            default_connect_arguments['port'] = self.__port
        if self.__password is not None:
            default_connect_arguments['password'] = self.__password
        if default_connect_arguments:
            default_connect_arguments.update(self.__kwargs)
            self.connect(**default_connect_arguments)

    @log.guard
    def connect(self, **kwargs: dict):
        if 'host' in kwargs:
            self.__host = kwargs['host']
            del kwargs['host']
        if 'port' in kwargs:
            self.__port = kwargs['port']
            del kwargs['port']
        if 'password' in kwargs:
            self.__password = kwargs['password']
            del kwargs['password']
        self.__kwargs = kwargs
        try:
            self.__connection_pool = redis.ConnectionPool(**kwargs)
            self.__redis_handle = redis.Redis(connection_pool=self.__connection_pool)
            self.__redis_handle.client_getname()
        except redis.ConnectionError:
            log.exception()
            self.__connection_pool = None
            self.__redis_handle = None

    def restore(self):
        self._default_connect()

    def alive(self):
        return self.__redis_handle is not None
