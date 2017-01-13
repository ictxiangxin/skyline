from skyline.setting import configure
from skyline.setting import log

configure = configure.dal.driver.driver_file


class File:
    def __init__(self, file: str=None, mode: str=None, encoding: str=configure.encoding):
        self.__file_pointer = None
        self.__arguments = {'file': file, 'mode': mode, 'encoding': encoding}
        self._default_open()

    def __del__(self):
        self.close()

    def __getattr__(self, item):
        def null(*args, **kwargs):
            pass
        if self.__file_pointer is None:
            self._default_open()
        if self.__file_pointer is not None:
            try:
                file_method = getattr(self.__file_pointer, item)
                if callable(file_method):
                    return self.guard(file_method)
            except AttributeError:
                log.warning('File has no such method: {}'.format(item))
                return null
        else:
            log.warning('File has not opened')
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
    def _default_open(self):
        if None not in (self.__arguments.get('file', None), self.__arguments.get('mode', None), self.__arguments.get('encoding', None)):
            self.open(**self.__arguments)

    @log.guard
    def open(self, file: str=None, mode: str=None, encoding: str=configure.encoding, **kwargs):
        kwargs['file'] = file
        kwargs['mode'] = mode
        kwargs['encoding'] = encoding
        self.__arguments = kwargs
        self.__file_pointer = open(**kwargs)

    @log.guard
    def close(self):
        try:
            if self.__file_pointer is not None:
                self.__file_pointer.close()
        finally:
            self.__file_pointer = None

    def restore(self):
        self._default_open()

    def alive(self):
        return self.__file_pointer is not None
