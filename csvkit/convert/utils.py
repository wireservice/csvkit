#!/usr/bin/env python

import csv
from cStringIO import StringIO

def rows_to_csv_string(rows):
    o = StringIO()
    writer = csv.writer(o, lineterminator='\n')
    writer.writerows(rows)
    output = o.getvalue()
    o.close()

    return output
