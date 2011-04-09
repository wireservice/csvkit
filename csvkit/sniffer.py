#!/usr/bin/env python

import csv

POSSIBLE_DELIMITERS = [',', '\t', ';', ' ', ':', '|']

def sniff_dialect(f):
    sample = f.read(4096)

    try:
        dialect = csv.Sniffer().sniff(sample, POSSIBLE_DELIMITERS)
    except:
        dialect = None

    f.seek(0)

    return dialect

