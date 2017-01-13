import sqlite3
from skyline.setting import log


class Sqlite:
    def __init__(self, database: str=None):
        self.__connection = None
        self.__arguments = {'database': database}
        self._default_connect()

    def __del__(self):
        self.close()

    def __getattr__(self, item):
        def null(*args, **kwargs):
            pass
        if self.__connection is None:
            self._default_connect()
        if self.__connection is not None:
            try:
                sqlite_method = getattr(self.__connection, item)
                if callable(sqlite_method):
                    return self.guard(sqlite_method)
            except AttributeError:
                log.warning('Sqlite has no such method: {}'.format(item))
                return null
        else:
            log.warning('Sqlite has not connected')
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
        if self.__arguments.get('database', None) is not None:
            self.connect(**self.__arguments)

    @log.guard
    def connect(self, **kwargs):
        self.__arguments = kwargs
        try:
            self.__connection = sqlite3.connect(**kwargs)
        except:
            self.__connection = None
            raise

    @log.guard
    def close(self):
        try:
            if self.__connection is not None:
                self.__connection.commit()
                self.__connection.close()
        finally:
            self.__connection = None

    def restore(self):
        self._default_connect()

    def alive(self):
        return self.__connection is not None
