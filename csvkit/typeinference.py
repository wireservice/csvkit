#!/usr/bin/env python

def infer_simple_type(l):
    """
    Given a list of strings, will attempt to determine if they are ints, floats, or strings.

    Returns an analogous list with elements of the inferred type.
    """
    try:
        return [int(x) for x in l]
    except:
        try:
            return [float(x) for x in l]
        except:
            return l

def infer_complex_type(l):
    """
    Like infer_simple_type, but will also attempt to infer dates, times, and datetimes. 
    """
    raise NotImplementedError()
