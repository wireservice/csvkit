#!/usr/bin/env python

from six import StringIO

from csvkit import CSVKitWriter

def psql2csv(f, key=None, **kwargs):
    """
    Convert psql (PostgresQL) ASCII table output into CSV format.
    """
    first_line = f.readline()
    crud = f.readline()

    splits = [ i
        for i, ch in enumerate(first_line)
            if ch == "|" ]

    bounds = list(zip([ -1 ] + splits, splits + [ None ]))

    def get_fields(line):
        return tuple(line[start + 1:end].strip()
            for start, end in bounds)

    if crud[:3] != "---":
        raise TypeError("Doesn't look like a Postgres ASCII table.")
    
    o = StringIO()
    writer = CSVKitWriter(o)

    writer.writerow(get_fields(first_line))

    for line in f:
        if "|" in line:
            writer.writerow(get_fields(line))

    output = o.getvalue()
    o.close()

    return output

