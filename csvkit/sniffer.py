#!/usr/bin/env python

import csv

POSSIBLE_DELIMITERS = [',', '\t', ';', ' ', ':', '|']

def sniff_dialect(sample, **kwargs):
    if 'snifflimit' in kwargs:
        sample = sample[:kwargs['snifflimit']]
        
    try:
        dialect = csv.Sniffer().sniff(sample, POSSIBLE_DELIMITERS)
    except:
        dialect = None

    return dialect

