#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

try:
    from mock import patch
except ImportError:
    from unittest.mock import patch

from csvkit.utilities.csvtranspose import CSVTranspose, launch_new_instance
from tests.utils import CSVKitTestCase


class TestCSVTranspose(CSVKitTestCase):
    Utility = CSVTranspose

    def test_launch_new_instance(self):
        with patch.object(sys, 'argv', [self.Utility.__name__.lower(), 'examples/dummy.csv']):
            launch_new_instance()

    def test_simple(self):
        self.assertRows(['examples/dummy.csv'], [
            ['a', '1'],
            ['b', '2'],
            ['c', '3'],
        ])
