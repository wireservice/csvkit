import io
import sys
from unittest.mock import patch

from csvkit.utilities.csvsort import CSVSort, launch_new_instance
from tests.utils import ColumnsTests, CSVKitTestCase, EmptyFileTests, NamesTests, stdin_as_string


class TestCSVSort(CSVKitTestCase, ColumnsTests, EmptyFileTests, NamesTests):
    Utility = CSVSort

    def test_launch_new_instance(self):
        with patch.object(sys, 'argv', [self.Utility.__name__.lower(), 'examples/dummy.csv']):
            launch_new_instance()

    def test_runs(self):
        self.assertRows(['examples/test_utf8.csv'], [
            ['foo', 'bar', 'baz'],
            ['1', '2', '3'],
            ['4', '5', 'ʤ'],
        ])

    def test_encoding(self):
        self.assertRows(['-e', 'latin1', 'examples/test_latin1.csv'], [
            ['a', 'b', 'c'],
            ['1', '2', '3'],
            ['4', '5', '©'],
        ])

    def test_sort_string_reverse(self):
        reader = self.get_output_as_reader(['-c', '1', '-r', 'examples/testxls_converted.csv'])
        test_order = ['text', 'Unicode! Σ', 'This row has blanks',
                      'Chicago Tribune', 'Chicago Sun-Times', 'Chicago Reader']
        new_order = [str(r[0]) for r in reader]
        self.assertEqual(test_order, new_order)

    def test_sort_date(self):
        reader = self.get_output_as_reader(['-c', '2', 'examples/testxls_converted.csv'])
        test_order = ['text', 'Chicago Tribune', 'Chicago Sun-Times',
                      'Chicago Reader', 'This row has blanks', 'Unicode! Σ']
        new_order = [str(r[0]) for r in reader]
        self.assertEqual(test_order, new_order)

    def test_mixed_sort_directions(self):
        data = b'group,value,label\nB,1,first\nA,2,second\nA,10,third\nB,3,fourth\nA,10,fifth\n'

        with stdin_as_string(io.BytesIO(data)):
            self.assertRows(['-c', 'group,~value'], [
                ['group', 'value', 'label'],
                ['A', '10', 'third'],
                ['A', '10', 'fifth'],
                ['A', '2', 'second'],
                ['B', '3', 'fourth'],
                ['B', '1', 'first'],
            ])

        with stdin_as_string(io.BytesIO(data)):
            self.assertRows(['-c', '0,~1', '--zero', '-r'], [
                ['group', 'value', 'label'],
                ['B', '1', 'first'],
                ['B', '3', 'fourth'],
                ['A', '2', 'second'],
                ['A', '10', 'third'],
                ['A', '10', 'fifth'],
            ])

        for args in (['-c', '~2,1'], ['--columns=~2,1'], ['-c~2,1']):
            with self.subTest(args=args), stdin_as_string(io.BytesIO(data)):
                self.assertRows(args, [
                    ['group', 'value', 'label'],
                    ['A', '10', 'third'],
                    ['A', '10', 'fifth'],
                    ['B', '3', 'fourth'],
                    ['A', '2', 'second'],
                    ['B', '1', 'first'],
                ])

    def test_mixed_sort_directions_with_nulls_and_ignore_case(self):
        data = b'group,value\nb,apple\nA,banana\na,Apple\nA,\n'

        with stdin_as_string(io.BytesIO(data)):
            self.assertRows(['-i', '-c', '1,~2'], [
                ['group', 'value'],
                ['A', ''],
                ['A', 'banana'],
                ['a', 'Apple'],
                ['b', 'apple'],
            ])

    def test_mixed_sort_directions_with_range(self):
        data = b'group,value,label\nA,2,b\nA,2,a\nA,10,c\nB,1,z\n'

        with stdin_as_string(io.BytesIO(data)):
            self.assertRows(['-c', '1,~2-3'], [
                ['group', 'value', 'label'],
                ['A', '10', 'c'],
                ['A', '2', 'b'],
                ['A', '2', 'a'],
                ['B', '1', 'z'],
            ])

    def test_column_name_starting_with_tilde(self):
        data = b'~priority,value\n2,second\n1,first\n'

        with stdin_as_string(io.BytesIO(data)):
            self.assertRows(['-c', '~priority'], [
                ['~priority', 'value'],
                ['1', 'first'],
                ['2', 'second'],
            ])

    def test_ignore_case(self):
        self.assertRows(['-i', 'examples/test_ignore_case.csv'], [
            ['a', 'b', 'c'],
            ['3', '2009-01-01', 'd'],
            ['20', '2001-01-01', 'c'],
            ['20', '2002-01-01', 'b'],
            ['100', '2003-01-01', 'a'],
            ['100', '2003-01-01', 'A'],
        ])

    def test_no_blanks(self):
        reader = self.get_output_as_reader(['examples/blanks.csv'])
        test_order = [
            ['a', 'b', 'c', 'd', 'e', 'f'],
            ['', '', '', '', '', ''],
        ]
        new_order = list(reader)
        self.assertEqual(test_order, new_order)

    def test_blanks(self):
        reader = self.get_output_as_reader(['--blanks', 'examples/blanks.csv'])
        test_order = [
            ['a', 'b', 'c', 'd', 'e', 'f'],
            ['', 'NA', 'N/A', 'NONE', 'NULL', '.'],
        ]
        new_order = list(reader)
        self.assertEqual(test_order, new_order)

    def test_no_header_row(self):
        self.assertRows(['--no-header-row', '--no-inference', 'examples/no_header_row.csv'], [
            ['a', 'b', 'c'],
            ['1', '2', '3'],
        ])

    def test_no_inference(self):
        reader = self.get_output_as_reader(['--no-inference', '-c', '1', 'examples/test_literal_order.csv'])
        test_order = ['a', '192', '27', '3']
        new_order = [str(r[0]) for r in reader]
        self.assertEqual(test_order, new_order)

    def test_sort_t_and_nulls(self):
        reader = self.get_output_as_reader(['-c', '2', 'examples/sort_ints_nulls.csv'])
        test_order = ['b', '1', '2', '']
        new_order = [str(r[1]) for r in reader]
        self.assertEqual(test_order, new_order)

    def test_stdin(self):
        input_file = io.BytesIO(b'a,b,c\n4,5,6\n1,2,3\n')

        with stdin_as_string(input_file):
            self.assertLines([], [
                'a,b,c',
                '1,2,3',
                '4,5,6',
            ])

        input_file.close()
