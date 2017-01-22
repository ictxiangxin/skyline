import io
from skyline.dal.driver import File
from skyline.setting import configure
from skyline.setting import log

configure = configure.dal.model.linear.abstract.file

_read_mode = 0
_write_mode = 1


class LinearFile:
    def __init__(self, file: str, append: bool=configure.append, encoding: str=configure.encoding):
        self.__file = file
        self.__append = append
        self.__encoding = encoding
        self.__driver = None
        self.__current_mode = _read_mode
        self._check(self.__current_mode)

    def __del__(self):
        self.close()

    def __iter__(self):
        return self

    def __next__(self):
        if self._check(_read_mode):
            row = self.read_row()
            if row is None:
                raise StopIteration
            else:
                return row
        else:
            raise StopIteration

    def _check(self, mode: int):
        if mode == _read_mode:
            open_mode = 'r'
        else:
            if self.__append:
                open_mode = 'a'
            else:
                open_mode = 'w'
        if self.__driver is None:
            self._reset(open_mode)
        else:
            if self.__current_mode != mode:
                self._reset(open_mode)
        if self.__driver is None:
            log.error('Can not init File driver')
            return False
        else:
            self.__current_mode = mode
            return True

    @log.guard
    def _reset(self, open_mode: str):
        if self.__driver is not None:
            self.__driver.close()
        self.__driver = File(self.__file, open_mode, self.__encoding)
        if not self.__driver.alive():
            self.__driver = None

    @log.guard
    def close(self):
        if self.__driver is not None:
            self.__driver.close()
            self.__driver = None

    @log.guard
    def read(self, size: int=-1):
        if self._check(_read_mode):
            data = self.__driver.read(size)
            return data

    @log.guard
    def read_rows(self, count: int=1):
        if self._check(_read_mode):
            data = self.__driver.readlines(count)
            return data

    @log.guard
    def read_row(self):
        rows = self.read_rows()
        return rows[0] if rows else None

    @log.guard
    def read_position(self, index: int, size: int=-1):
        if self._check(_read_mode):
            self.__driver.flush()
            read_position = self.__driver.tell()
            self.__driver.seek(index, io.SEEK_SET)
            data = self.__driver.read(size)
            self.__driver.flush()
            self.__driver.seek(read_position, io.SEEK_SET)
            return data

    @log.guard
    def write(self, data: str):
        if self._check(_write_mode):
            self.__driver.write(data)

    @log.guard
    def write_rows(self, data_list: list):
        if self._check(_write_mode):
            self.__driver.writelines(data_list)

    @log.guard
    def write_position(self, index: int, data: str):
        if self._check(_write_mode):
            self.__driver.flush()
            write_position = self.__driver.tell()
            self.__driver.seek(index, io.SEEK_SET)
            self.__driver.write(data)
            self.__driver.flush()
            self.__driver.seek(write_position, io.SEEK_SET)
