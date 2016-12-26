#!/usr/bin/env python

import six

from csvkit.convert import fixed
from csvkit.utilities.in2csv import In2CSV
from tests.utils import CSVKitTestCase, stdin_as_string


class TestFixed(CSVKitTestCase):
    Utility = In2CSV

    def test_fixed(self):
        with open('examples/testfixed', 'r') as f:
            with open('examples/testfixed_schema.csv', 'r') as schema:
                output = fixed.fixed2csv(f, schema)

        with open('examples/testfixed_converted.csv', 'r') as f:
            self.assertEqual(f.read(), output)

    def test_fixed_no_inference(self):
        input_file = six.StringIO('     1   2 3')

        with stdin_as_string(input_file):
            self.assertLines(['--no-inference', '-f', 'fixed', '--schema', 'examples/testfixed_schema_no_inference.csv'], [
                'a,b,c',
                '1,2,3',
            ])

        input_file.close()

    def test_fixed_streaming(self):
        with open('examples/testfixed', 'r') as f:
            with open('examples/testfixed_schema.csv', 'r') as schema:
                output_file = six.StringIO()
                fixed.fixed2csv(f, schema, output=output_file)
                output = output_file.getvalue()
                output_file.close()

        with open('examples/testfixed_converted.csv', 'r') as f:
            self.assertEqual(f.read(), output)

    def test_schema_decoder_init(self):
        rd = fixed.SchemaDecoder(['column', 'start', 'length'])
        self.assertEqual(1, rd.start)
        self.assertEqual(2, rd.length)
        self.assertEqual(0, rd.column)

    def test_schema_decoder_in_action(self):
        rd = fixed.SchemaDecoder(['comment', 'start', 'length', 'column'])

        (column, start, length) = rd(['This is a comment', '0', '1', 'column_name'])
        self.assertEqual(False, rd.one_based)
        self.assertEqual('column_name', column)
        self.assertEqual(0, start)
        self.assertEqual(1, length)

        (column, start, length) = rd(['This is another comment', '1', '5', 'column_name2'])
        self.assertEqual(False, rd.one_based)
        self.assertEqual('column_name2', column)
        self.assertEqual(1, start)
        self.assertEqual(5, length)

        (column, start, length) = rd(['yet another comment', '9', '14', 'column_name3'])
        self.assertEqual(False, rd.one_based)
        self.assertEqual('column_name3', column)
        self.assertEqual(9, start)
        self.assertEqual(14, length)

    def test_one_based_row_decoder(self):
        rd = fixed.SchemaDecoder(['column', 'start', 'length'])

        (column, start, length) = rd(['LABEL', '1', '5'])
        self.assertEqual(True, rd.one_based)
        self.assertEqual('LABEL', column)
        self.assertEqual(0, start)
        self.assertEqual(5, length)

        (column, start, length) = rd(['LABEL2', '6', '15'])
        self.assertEqual('LABEL2', column)
        self.assertEqual(5, start)
        self.assertEqual(15, length)

    def test_schematic_line_parser(self):
        schema = """column,start,length
foo,1,5
bar,6,2
baz,8,5"""

        f = six.StringIO(schema)
        parser = fixed.FixedWidthRowParser(f)
        f.close()

        self.assertEqual('foo', parser.headers[0])
        self.assertEqual('bar', parser.headers[1])
        self.assertEqual('baz', parser.headers[2])

        parsed = parser.parse("111112233333")
        self.assertEqual('11111', parsed[0])
        self.assertEqual('22', parsed[1])
        self.assertEqual('33333', parsed[2])

        parsed = parser.parse("    1 2    3")
        self.assertEqual('1', parsed[0])
        self.assertEqual('2', parsed[1])
        self.assertEqual('3', parsed[2])

        parsed = parser.parse("1  1  233  3")
        self.assertEqual('1  1', parsed[0])
        self.assertEqual('2', parsed[1])
        self.assertEqual('33  3', parsed[2])
