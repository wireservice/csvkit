#!/usr/bin/env python

import csv

POSSIBLE_DELIMITERS = [',', '\t', ';', ' ', ':', '|']

def sniff_dialect(sample):
    try:
        dialect = csv.Sniffer().sniff(sample, POSSIBLE_DELIMITERS)
    except:
        dialect = None

    return dialect

