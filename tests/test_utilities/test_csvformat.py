#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

import six

try:
    from mock import patch
except ImportError:
    from unittest.mock import patch

from csvkit.utilities.csvformat import CSVFormat, launch_new_instance
from tests.utils import CSVKitTestCase, stdin_as_string


class TestCSVFormat(CSVKitTestCase):
    Utility = CSVFormat

    def test_launch_new_instance(self):
        with patch.object(sys, 'argv', ['csvformat', 'examples/dummy.csv']):
            launch_new_instance()

    def test_delimiter(self):
        self.assertLines(['-D', '|', 'examples/dummy.csv'], [
            'a|b|c',
            '1|2|3',
        ])

    def test_tab_delimiter(self):
        self.assertLines(['-T', 'examples/dummy.csv'], [
            'a\tb\tc',
            '1\t2\t3',
        ])

    def test_quoting(self):
        input_file = six.StringIO('a,b,c\n1*2,3,4\n')

        with stdin_as_string(input_file):
            self.assertLines(['-Q', '*', '-U', '0', '-B'], [
                'a,b,c',
                '*1**2*,3,4',
            ])

    def test_escapechar(self):
        input_file = six.StringIO('a,b,c\n1"2,3,4\n')

        with stdin_as_string(input_file):
            self.assertLines(['-P', '#', '-U', '3'], [
                'a,b,c',
                '1#"2,3,4',
            ])

    def test_lineterminator(self):
        self.assertLines(['-M', 'XYZ', 'examples/dummy.csv'], [
            'a,b,cXYZ1,2,3XYZ',
        ])
