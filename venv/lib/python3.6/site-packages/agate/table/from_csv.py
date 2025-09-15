import io
import itertools
import sys


@classmethod
def from_csv(cls, path, column_names=None, column_types=None, row_names=None, skip_lines=0, header=True, sniff_limit=0,
             encoding='utf-8', row_limit=None, **kwargs):
    """
    Create a new table from a CSV.

    This method uses agate's builtin CSV reader, which supplies encoding
    support for both Python 2 and Python 3.

    :code:`kwargs` will be passed through to the CSV reader.

    :param path:
        Filepath or file-like object from which to read CSV data. If a file-like
        object is specified, it must be seekable. If using Python 2, the file
        should be opened in binary mode (`rb`).
    :param column_names:
        See :meth:`.Table.__init__`.
    :param column_types:
        See :meth:`.Table.__init__`.
    :param row_names:
        See :meth:`.Table.__init__`.
    :param skip_lines:
        The number of lines to skip from the top of the file.
    :param header:
        If :code:`True`, the first row of the CSV is assumed to contain column
        names. If :code:`header` and :code:`column_names` are both specified
        then a row will be skipped, but :code:`column_names` will be used.
    :param sniff_limit:
        Limit CSV dialect sniffing to the specified number of bytes. Set to
        None to sniff the entire file. Defaults to 0 (no sniffing).
    :param encoding:
        Character encoding of the CSV file. Note: if passing in a file
        handle it is assumed you have already opened it with the correct
        encoding specified.
    :param row_limit:
        Limit how many rows of data will be read.
    """
    from agate import csv
    from agate.table import Table

    close = False

    try:
        if hasattr(path, 'read'):
            f = path
        else:
            f = open(path, encoding=encoding)

            close = True

        if isinstance(skip_lines, int):
            while skip_lines > 0:
                f.readline()
                skip_lines -= 1
        else:
            raise ValueError('skip_lines argument must be an int')

        handle = f

        if sniff_limit is None:
            # Overwrite `handle` to not read the file a second time in `csv.reader`.
            handle = io.StringIO(f.read())
            sample = handle.getvalue()
        elif sniff_limit > 0:
            if f == sys.stdin:
                # "At most one single read on the raw stream is done to satisfy the call. The number of bytes returned
                # may be less or more than requested." In other words, it reads the buffer_size, which might be less or
                # more than the sniff_limit. On my machine, the buffer_size of sys.stdin.buffer is the length of the
                # input, up to 65536. This assumes that users don't sniff more than 64 KiB.
                # https://docs.python.org/3/library/io.html#io.BufferedReader.peek
                sample = f.buffer.peek(sniff_limit).decode(encoding, 'ignore')[:sniff_limit]  # reads *bytes*
            else:
                offset = f.tell()
                sample = f.read(sniff_limit)  # reads *characters*
                f.seek(offset)  # can't do f.seek(-sniff_limit, os.SEEK_CUR) on file opened in text mode

        if sniff_limit is None or sniff_limit > 0:
            kwargs['dialect'] = csv.Sniffer().sniff(sample)

        reader = csv.reader(handle, header=header, **kwargs)

        if header:
            if column_names is None:
                column_names = next(reader)
            else:
                next(reader)

        if row_limit is None:
            rows = reader
        else:
            rows = itertools.islice(reader, row_limit)

        return Table(rows, column_names, column_types, row_names=row_names)
    finally:
        if close:
            f.close()
