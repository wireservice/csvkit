#!/usr/bin/env python

import StringIO
import unittest

from csvkit import CSVKitReader
from csvkit.utilities.csvsplit import CSVSplit, fname_format

class DummyFiles(object):
    def __init__(self):
        self.file_objs = {}
    
    def dummy_file_constructor(self, fname, mode, *args, **kwargs):
        fobj = StringIO.StringIO()
        self.file_objs[fname] = fobj
        return fobj

class TestCSVSplit(unittest.TestCase):
    def test_fname(self):
        output_fname = fname_format("data/population.projection.csv", "2009")
        self.assertEqual(output_fname, "data/population.projection_2009.csv")

    def test_explicit_splitting(self):
        # Split a file in two files
        args = ['-c', 'foo', 'examples/dummy-stacked.csv']
        utility = CSVSplit(args)


        dummy_files = DummyFiles()
        utility.main(dummy_files.dummy_file_constructor)
        print dummy_files.file_objs

        input_file = StringIO.StringIO(dummy_files.file_objs[('examples/dummy-stacked_asd.csv')].getvalue())
        reader = CSVKitReader(input_file)
        self.assertEqual(reader.next(), ['foo', 'a', 'b', 'c'])
        self.assertEqual(reader.next(), ['asd', '1', '2', '3'])
        self.assertEqual(reader.next(), ['asd', '4', '5', '6'])

        input_file = StringIO.StringIO(dummy_files.file_objs[('examples/dummy-stacked_sdf.csv')].getvalue())
        reader = CSVKitReader(input_file)
        self.assertEqual(reader.next(), ['foo', 'a', 'b', 'c'])
        self.assertEqual(reader.next(), ['sdf', '1', '2', '3'])
        self.assertEqual(reader.next(), ['sdf', '4', '5', '6'])

    def test_no_header_row(self):
        # Split a file in two files
        args = ['-c', '1', '--no-header-row', 'examples/dummy-stacked.csv']
        utility = CSVSplit(args)

        dummy_files = DummyFiles()
        utility.main(dummy_files.dummy_file_constructor)
        print dummy_files.file_objs

        input_file = StringIO.StringIO(dummy_files.file_objs[('examples/dummy-stacked_foo.csv')].getvalue())
        reader = CSVKitReader(input_file)
        self.assertEqual(reader.next(), ['column1', 'column2', 'column3', 'column4'])
        self.assertEqual(reader.next(), ['foo', 'a', 'b', 'c'])

        input_file = StringIO.StringIO(dummy_files.file_objs[('examples/dummy-stacked_asd.csv')].getvalue())
        reader = CSVKitReader(input_file)
        self.assertEqual(reader.next(), ['column1', 'column2', 'column3', 'column4'])
        self.assertEqual(reader.next(), ['asd', '1', '2', '3'])
        self.assertEqual(reader.next(), ['asd', '4', '5', '6'])

        input_file = StringIO.StringIO(dummy_files.file_objs[('examples/dummy-stacked_sdf.csv')].getvalue())
        reader = CSVKitReader(input_file)
        self.assertEqual(reader.next(), ['column1', 'column2', 'column3', 'column4'])
        self.assertEqual(reader.next(), ['sdf', '1', '2', '3'])
        self.assertEqual(reader.next(), ['sdf', '4', '5', '6'])
