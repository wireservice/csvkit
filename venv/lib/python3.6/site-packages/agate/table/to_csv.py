import os


def to_csv(self, path, **kwargs):
    """
    Write this table to a CSV. This method uses agate's builtin CSV writer,
    which supports unicode on both Python 2 and Python 3.

    ``kwargs`` will be passed through to the CSV writer.

    The ``lineterminator`` defaults to the newline character (LF, ``\\n``).

    :param path:
        Filepath or file-like object to write to.
    """
    from agate import csv

    if 'lineterminator' not in kwargs:
        kwargs['lineterminator'] = '\n'

    close = True
    f = None

    try:
        if hasattr(path, 'write'):
            f = path
            close = False
        else:
            dirpath = os.path.dirname(path)

            if dirpath and not os.path.exists(dirpath):
                os.makedirs(dirpath)

            f = open(path, 'w')

        writer = csv.writer(f, **kwargs)
        writer.writerow(self._column_names)

        csv_funcs = [c.csvify for c in self._column_types]

        for row in self._rows:
            writer.writerow(tuple(csv_funcs[i](d) for i, d in enumerate(row)))
    finally:
        if close and f is not None:
            f.close()
