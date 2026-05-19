"""
Reads data from FPT (memo) files.

FPT files are used to varying lenght text or binary data which is too
large to fit in a DBF field.

VFP == Visual FoxPro
DB3 == dBase III
DB4 == dBase IV
"""
from collections import namedtuple
from .ifiles import ifind
from .struct_parser import StructParser



VFPFileHeader = StructParser(
    'FPTHeader',
    '>LHH504s',
    ['nextblock',
     'reserved1',
     'blocksize',
     'reserved2'])

VFPMemoHeader = StructParser(
    'FoxProMemoHeader',
    '>LL',
    ['type',
     'length'])

DB4MemoHeader = StructParser(
    'DBase4MemoHeader',
    '<LL',
    ['reserved',  # Always 0xff 0xff 0x08 0x08.
     'length'])

# Used for Visual FoxPro memos to distinguish binary from text memos.

class VFPMemo(bytes):
    pass

class BinaryMemo(VFPMemo):
    pass

class PictureMemo(BinaryMemo):
    pass

class ObjectMemo(BinaryMemo):
    pass

class TextMemo(VFPMemo):
    pass


VFP_TYPE_MAP = {
    0x0: PictureMemo,
    0x1: TextMemo,
    0x2: ObjectMemo,
}


class MemoFile(object):
    def __init__(self, filename):
        self.filename = filename
        self._open()
        self._init()

    def _init(self):
        pass

    def _open(self):
        self.file = open(self.filename, 'rb')
        # Shortcuts for speed.
        self._read = self.file.read
        self._seek = self.file.seek

    def _close(self):
        self.file.close()

    def __getitem__(self, index):
        raise NotImplemented

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self._close()
        return False


class FakeMemoFile(MemoFile):
    def __getitem__(self, i):
        return None

    def _open(self):
        pass

    _init = _close = _open


class VFPMemoFile(MemoFile):
    def _init(self):
        self.header = VFPFileHeader.read(self.file)

    def __getitem__(self, index):
        """Get a memo from the file."""
        if index <= 0:
            return None

        self._seek(index * self.header.blocksize)
        memo_header = VFPMemoHeader.read(self.file)

        data = self._read(memo_header.length)
        if len(data) != memo_header.length:
            raise IOError('EOF reached while reading memo')
        
        return VFP_TYPE_MAP.get(memo_header.type, BinaryMemo)(data)


class DB3MemoFile(MemoFile):
    """dBase III memo file."""
    # Code from dbf.py
    def __getitem__(self, index):
        if index <= 0:
            return None

        block_size = 512
        self._seek(index * block_size)
        data = b''
        while True:
            newdata = self._read(block_size)
            if not newdata:
                return data
            data += newdata

            # Todo: some files (help.dbt) has only one field separator.
            # Is this enough for all file though?
            end_of_memo = data.find(b'\x1a')
            if end_of_memo != -1:
                return data[:end_of_memo]

            # Alternative end of memo markers:
            # \x1a\x1a
            # \x0d\x0a

        return data[:eom]        

class DB4MemoFile(MemoFile):
    """dBase IV memo file"""
    def __getitem__(self, index):
        if index <= 0:
            return None

        # Todo: read this from the file header.
        block_size = 512

        self._seek(index * block_size)
        memo_header = DB4MemoHeader.read(self.file)
        data = self._read(memo_header.length)
        # Todo: fields are terminated in different ways.
        # \x1a is one of them
        # \x1f seems to be another (dbase_8b.dbt)
        return data.split(b'\x1f', 1)[0]


def find_memofile(dbf_filename):
    for ext in ['.fpt', '.dbt']:
        name = ifind(dbf_filename, ext=ext)
        if name:
            return name
    else:
        return None


def open_memofile(filename, dbversion):
    if filename.lower().endswith('.fpt'):
        return VFPMemoFile(filename)
    else:
        # print('######', dbversion)
        if dbversion == 0x83:
            return DB3MemoFile(filename)
        else:
            return DB4MemoFile(filename)
