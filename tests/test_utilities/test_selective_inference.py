import io
import json
import sys
from contextlib import redirect_stderr
from decimal import Decimal
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import agate
from openpyxl import Workbook

from csvkit.exceptions import ColumnIdentifierError
from csvkit.utilities.csvjoin import CSVJoin
from csvkit.utilities.csvjson import CSVJSON
from csvkit.utilities.csvlook import CSVLook
from csvkit.utilities.csvpy import CSVPy
from csvkit.utilities.csvsort import CSVSort
from csvkit.utilities.csvsql import CSVSQL
from csvkit.utilities.csvstat import CSVStat
from csvkit.utilities.in2csv import In2CSV
from tests.utils import CSVKitTestCase, stdin_as_string

DATA = 'id,amount,date,active\n2,10,01/02/2024,true\n10,2,03/04/2024,false\n001,3,05/06/2024,true\n'
SELECTIVE = ['--no-inference-columns', 'id,date', '--date-format', '%m/%d/%Y']


class InputMixin:
    def output(self, args, data=DATA):
        with stdin_as_string(io.BytesIO(data.encode('utf-8'))):
            return self.get_output(['-y', '0'] + args)

    def rows(self, args, data=DATA):
        return list(agate.csv.reader(io.StringIO(self.output(args, data))))


class TestSelectiveCSVJSON(InputMixin, CSVKitTestCase):
    Utility = CSVJSON

    def test_selective_names_and_types(self):
        rows = json.loads(self.output(SELECTIVE))
        self.assertEqual(rows[2], {'id': '001', 'amount': 3, 'date': '05/06/2024', 'active': True})

    def test_selective_ids_ranges_and_zero(self):
        for args in (
            ['--no-inference-columns', '1-2'],
            ['--zero', '--no-inference-columns', '0-1'],
        ):
            with self.subTest(args=args):
                row = json.loads(self.output(args + ['--date-format', '%m/%d/%Y']))[2]
                self.assertEqual(row, {'id': '001', 'amount': '3', 'date': '2024-05-06', 'active': True})

    def test_selective_headerless(self):
        rows = json.loads(self.output(['-H', '--zero', '--no-inference-columns', '0'], '001,2\n002,3\n'))
        self.assertEqual(rows, [{'a': '001', 'b': 2}, {'a': '002', 'b': 3}])

    def test_selective_nulls(self):
        for options, expected in (
            ([], None),
            (['--blanks'], 'NA'),
            (['--null-value', 'MISSING'], None),
            (['--blanks', '--null-value', 'MISSING'], 'NA'),
        ):
            with self.subTest(options=options):
                row = json.loads(self.output(['--no-inference-columns', 'id'] + options,
                                             'id,amount\nNA,2\n001,3\n'))[0]
                self.assertEqual(row, {'id': expected, 'amount': 2})
        row = json.loads(self.output(['--no-inference-columns', 'id', '--null-value', 'MISSING'],
                                     'id,amount\nMISSING,2\n001,3\n'))[0]
        self.assertEqual(row, {'id': None, 'amount': 2})

    def test_selective_stream_keeps_unselected_inference(self):
        rows = [json.loads(line) for line in self.output(['--stream'] + SELECTIVE).splitlines()]
        self.assertEqual(rows[2], {'id': '001', 'amount': 3, 'date': '05/06/2024', 'active': True})

    def test_selective_unknown_column(self):
        with self.assertRaises(ColumnIdentifierError):
            self.output(['--no-inference-columns', 'missing'])

    def test_selective_conflicts_with_global(self):
        for utility in (CSVJoin, CSVJSON, CSVLook, CSVPy, CSVSort, CSVSQL, CSVStat, In2CSV):
            with self.subTest(utility=utility.__name__), redirect_stderr(io.StringIO()) as stderr:
                with self.assertRaises(SystemExit) as error:
                    utility(['-I', '--no-inference-columns', 'id'])
                self.assertEqual(error.exception.code, 2)
                self.assertIn('not allowed with argument', stderr.getvalue())

    def test_legacy_default_and_global(self):
        row = json.loads(self.output(['--date-format', '%m/%d/%Y']))[2]
        self.assertEqual(row, {'id': 1, 'amount': 3, 'date': '2024-05-06', 'active': True})
        row = json.loads(self.output(['--no-inference']))[2]
        self.assertEqual(row, {'id': '001', 'amount': '3', 'date': '05/06/2024', 'active': 'true'})

    def test_legacy_global_stream_shortcut(self):
        with patch.object(CSVJSON, 'read_csv_to_table', side_effect=AssertionError('buffered input')):
            rows = [json.loads(line) for line in self.output(['--stream', '-I']).splitlines()]
        self.assertEqual(rows[2]['id'], '001')
        self.assertEqual(rows[2]['amount'], '3')

    def test_legacy_global_does_not_consume_filename(self):
        with TemporaryDirectory() as directory:
            filename = Path(directory) / 'input.csv'
            filename.write_text(DATA, encoding='utf-8')
            row = json.loads(self.get_output(['--no-inference', str(filename)]))[2]
        self.assertEqual(row['id'], '001')


class TestSelectiveCSVSort(InputMixin, CSVKitTestCase):
    Utility = CSVSort

    def test_selective_text_sort(self):
        rows = self.rows(['-c', 'id'] + SELECTIVE)
        self.assertEqual([row[0] for row in rows[1:]], ['001', '10', '2'])

    def test_selective_other_columns_sort_numerically(self):
        rows = self.rows(['-c', 'amount'] + SELECTIVE)
        self.assertEqual([row[0] for row in rows[1:]], ['10', '001', '2'])

    def test_legacy_default_sort(self):
        rows = self.rows(['-c', 'id'])
        self.assertEqual([row[0] for row in rows[1:]], ['1', '2', '10'])


class TestSelectiveCSVStat(InputMixin, CSVKitTestCase):
    Utility = CSVStat

    def test_selective_types(self):
        rows = json.loads(self.output(['--json'] + SELECTIVE))
        self.assertEqual({row['column_name']: row['type'] for row in rows},
                         {'id': 'Text', 'amount': 'Number', 'date': 'Text', 'active': 'Boolean'})


class TestSelectiveCSVLook(InputMixin, CSVKitTestCase):
    Utility = CSVLook

    def test_selective_display(self):
        output = self.output(SELECTIVE)
        self.assertIn('001', output)
        self.assertIn('05/06/2024', output)
        self.assertIn('True', output)


class TestSelectiveCSVSQL(InputMixin, CSVKitTestCase):
    Utility = CSVSQL

    def test_selective_schema(self):
        output = self.output(['--dialect', 'sqlite', '--tables', 'data'] + SELECTIVE)
        self.assertIn('id VARCHAR', output)
        self.assertIn('amount FLOAT', output)
        self.assertIn('date VARCHAR', output)
        self.assertIn('active BOOLEAN', output)

    def test_selective_sqlite_query(self):
        rows = self.rows(['--tables', 'data', '--query',
                          'SELECT id, amount FROM data ORDER BY amount'] + SELECTIVE)
        self.assertEqual(rows, [['id', 'amount'], ['10', '2.0'], ['001', '3.0'], ['2', '10.0']])


class TestSelectiveCSVJoin(CSVKitTestCase):
    Utility = CSVJoin

    def join(self, args, left, right):
        with TemporaryDirectory() as directory:
            paths = [Path(directory) / f'{name}.csv' for name in ('left', 'right')]
            for path, content in zip(paths, (left, right)):
                path.write_text(content, encoding='utf-8')
            return list(self.get_output_as_reader(['-y', '0'] + args + [str(path) for path in paths]))

    def test_selective_names_resolve_per_input(self):
        rows = self.join(['-c', 'id', '--no-inference-columns', 'id'],
                         'id,amount\n001,2\n002,3\n', 'amount,id\n10,001\n20,002\n')
        self.assertEqual(rows[1:], [['001', '2', '10'], ['002', '3', '20']])

    def test_selective_ids_do_not_leak_forced_names(self):
        rows = self.join(['--no-inference-columns', '1'],
                         'id,amount\n001,2\n002,3\n', 'amount,id\n010,009\n020,008\n')
        self.assertEqual(rows[1:], [['001', '2', '010', '9'], ['002', '3', '020', '8']])


class TestSelectiveIn2CSV(InputMixin, CSVKitTestCase):
    Utility = In2CSV

    def test_selective_csv_keeps_unselected_inference(self):
        rows = self.rows(['-f', 'csv'] + SELECTIVE)
        self.assertEqual(rows[3], ['001', '3', '05/06/2024', 'True'])

    def test_selective_ndjson(self):
        data = '\n'.join(json.dumps(dict(zip(('id', 'amount', 'date', 'active'), row))) for row in (
            ('001', '2', '01/02/2024', 'true'), ('002', '3', '03/04/2024', 'false'),
        ))
        rows = self.rows(['-f', 'ndjson'] + SELECTIVE, data)
        self.assertEqual(rows[1:], [['001', '2', '01/02/2024', 'True'], ['002', '3', '03/04/2024', 'False']])

    def test_selective_xlsx(self):
        with TemporaryDirectory() as directory:
            filename = Path(directory) / 'input.xlsx'
            workbook = Workbook()
            worksheet = workbook.active
            worksheet.append(['id', 'amount', 'date', 'active'])
            worksheet.append(['001', 2, '01/02/2024', 'true'])
            worksheet.append(['002', 3, '03/04/2024', 'false'])
            workbook.save(filename)
            workbook.close()
            rows = list(self.get_output_as_reader(SELECTIVE + [str(filename)]))
        self.assertEqual(rows[1:], [['001', '2', '01/02/2024', 'True'], ['002', '3', '03/04/2024', 'False']])

    def test_legacy_csv_stream_shortcut(self):
        with patch.object(agate.Table, 'from_csv', side_effect=AssertionError('buffered input')):
            rows = self.rows(['-f', 'csv', '-I'])
        self.assertEqual(rows[3], ['001', '3', '05/06/2024', 'true'])


class TestSelectiveCSVPy(CSVKitTestCase):
    Utility = CSVPy

    def test_selective_agate_table(self):
        with TemporaryDirectory() as directory:
            filename = Path(directory) / 'input.csv'
            filename.write_text(DATA, encoding='utf-8')
            with patch.dict(sys.modules, {'IPython.frontend.terminal.embed': None}), \
                    patch('code.interact') as interact:
                self.get_output(['--agate', '--zero', '--no-inference-columns', '0,2',
                                 '--date-format', '%m/%d/%Y', str(filename)])
            table = interact.call_args.kwargs['local']['table']
        self.assertEqual(tuple(table.rows[2]), ('001', Decimal('3'), '05/06/2024', True))
        self.assertEqual(tuple(type(column_type) for column_type in table.column_types),
                         (agate.Text, agate.Number, agate.Text, agate.Boolean))
