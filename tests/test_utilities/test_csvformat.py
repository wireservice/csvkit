#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

import six

try:
    from mock import patch
except ImportError:
    from unittest.mock import patch

from csvkit.utilities.csvformat import CSVFormat, launch_new_instance
from tests.utils import CSVKitTestCase, EmptyFileTests, stdin_as_string


class TestCSVFormat(CSVKitTestCase, EmptyFileTests):
    Utility = CSVFormat

    def test_launch_new_instance(self):
        with patch.object(sys, 'argv', [self.Utility.__name__.lower(), 'examples/dummy.csv']):
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

    def test_quotechar(self):
        input_file = six.StringIO('a,b,c\n1*2,3,4\n')

        with stdin_as_string(input_file):
            self.assertLines(['-Q', '*'], [
                'a,b,c',
                '*1**2*,3,4',
            ])

        input_file.close()

    def test_doublequote(self):
        input_file = six.StringIO('a\n"a ""quoted"" string"')

        with stdin_as_string(input_file):
            self.assertLines(['-P', '#', '-B'], [
                'a',
                'a #"quoted#" string',
            ])

        input_file.close()

    def test_escapechar(self):
        input_file = six.StringIO('a,b,c\n1"2,3,4\n')

        with stdin_as_string(input_file):
            self.assertLines(['-P', '#', '-U', '3'], [
                'a,b,c',
                '1#"2,3,4',
            ])

        input_file.close()

    def test_lineterminator(self):
        self.assertLines(['-M', 'XYZ', 'examples/dummy.csv'], [
            'a,b,cXYZ1,2,3XYZ',
        ], newline_at_eof=False)
