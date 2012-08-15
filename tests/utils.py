#!/usr/bin/env python

from contextlib import contextmanager
import sys

@contextmanager
def stderr_as_stdout():
    temp = sys.stderr
    sys.stderr = sys.stdout
    yield
    sys.stderr = temp

