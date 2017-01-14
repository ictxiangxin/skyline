import io
from skyline.dal.driver import File
from skyline.setting import configure
from skyline.setting import log

configure = configure.dal.model.linear.abstract.file

_read_mode = 0
_write_mode = 1


class LinearFile:
    def __init__(self, file: str, append: bool=configure.append, encoding: str=configure.encoding):
        self.__file = None
        self.__append = None
        self.__encoding = None
        self.__mode = None
        self.__driver = None
        self.__read_position = 0
        self.__write_position = 0
        self.__last_mode = _read_mode
        self.reset(file, append, encoding)

    def _check(self):
        if self.__driver is None:
            self.reset(self.__file, self.__append, self.__encoding)
        if self.__driver is None:
            log.error('Can not init File driver')
            return False
        else:
            return True

    @log.guard
    def reset(self, file: str, append: bool=configure.append, encoding: str=configure.encoding):
        self.__file = file
        self.__append = append
        self.__encoding = encoding
        if self.__append:
            self.__mode = 'a+'
        else:
            self.__mode = 'w+'
        if self.__driver is not None:
            self.__driver.close()
        self.__driver = File(self.__file, self.__mode, self.__encoding)
        if not self.__driver.alive():
            self.__driver = None
        else:
            self.__write_position = self.__driver.tell()

    @log.guard
    def read(self, size: int=-1):
        if self._check():
            if self.__last_mode == _write_mode:
                print(self.__read_position)
                self.__driver.seek(self.__read_position, io.SEEK_SET)
                self.__last_mode = _read_mode
            data = self.__driver.read(size)
            self.__driver.flush()
            self.__read_position = self.__driver.tell()
            print(self.__read_position)
            return data

    @log.guard
    def read_rows(self, count: int=1):
        if self._check():
            if self.__last_mode == _write_mode:
                print(self.__read_position)
                self.__driver.seek(self.__read_position, io.SEEK_SET)
                self.__last_mode = _read_mode
            data = self.__driver.readlines(count)
            self.__driver.flush()
            self.__read_position = self.__driver.tell()
            print(self.__read_position)
            return data

    @log.guard
    def read_row(self):
        return self.read_rows()[0]

    @log.guard
    def read_position(self, index: int, size: int=-1):
        if self._check():
            self.__driver.seek(index, io.SEEK_SET)
            data = self.__driver.read(size)
            self.__driver.flush()
            self.__driver.seek(self.__read_position, io.SEEK_SET)
            return data

    @log.guard
    def write(self, data: str):
        if self._check():
            if self.__last_mode == _read_mode:
                self.__driver.seek(self.__write_position, io.SEEK_SET)
                self.__last_mode = _write_mode
            self.__driver.write(data)
            self.__driver.flush()
            self.__write_position = self.__driver.tell()

    @log.guard
    def write_rows(self, data_list: list):
        if self._check():
            if self.__last_mode == _read_mode:
                self.__driver.seek(self.__write_position, io.SEEK_SET)
                self.__last_mode = _write_mode
            self.__driver.writelines(data_list)
            self.__driver.flush()
            self.__write_position = self.__driver.tell()

    @log.guard
    def write_position(self, index: int, data: str):
        if self._check():
            self.__driver.seek(index, io.SEEK_SET)
            self.__driver.write(data)
            self.__driver.flush()
            self.__driver.seek(self.__write_position, io.SEEK_SET)
