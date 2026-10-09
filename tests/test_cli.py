import datetime
import decimal
import io
import unittest
from contextlib import redirect_stderr

import agate

from csvkit.cli import ColumnIdentifierError, CSVKitUtility, match_column_identifier, parse_column_identifiers
from csvkit.utilities.csvsort import CSVSort


class TestCli(unittest.TestCase):

    def setUp(self):
        self.headers = ['id', 'name', 'i_work_here', '1', 'more-header-values', 'stuff', 'blueberry']

    def test_match_column_identifier_string(self):
        self.assertEqual(2, match_column_identifier(self.headers, 'i_work_here'))
        self.assertEqual(2, match_column_identifier(self.headers, 'i_work_here', column_offset=0))

    def test_match_column_identifier_numeric(self):
        self.assertEqual(2, match_column_identifier(self.headers, 3))
        self.assertEqual(3, match_column_identifier(self.headers, 3, column_offset=0))

    def test_match_column_which_could_be_integer_name_is_treated_as_positional_id(self):
        self.assertEqual(0, match_column_identifier(self.headers, '1'))
        self.assertEqual(1, match_column_identifier(self.headers, '1', column_offset=0))

    def test_parse_column_identifiers(self):
        self.assertEqual([2, 0, 1], parse_column_identifiers('i_work_here,1,name', self.headers))
        self.assertEqual([2, 1, 1], parse_column_identifiers('i_work_here,1,name', self.headers, column_offset=0))
        self.assertEqual(
            [1, 1],
            parse_column_identifiers(
                'i_work_here,1,name',
                self.headers,
                column_offset=0,
                excluded_columns='i_work_here,foobar',
            ),
        )

    def test_range_notation(self):
        self.assertEqual([0, 1, 2], parse_column_identifiers('1:3', self.headers))
        self.assertEqual([1, 2, 3], parse_column_identifiers('1:3', self.headers, column_offset=0))
        self.assertEqual([1, 2, 3], parse_column_identifiers('2-4', self.headers))
        self.assertEqual([2, 3, 4], parse_column_identifiers('2-4', self.headers, column_offset=0))
        self.assertEqual([0, 1, 2, 3], parse_column_identifiers('1,2:4', self.headers))
        self.assertEqual([1, 2, 3, 4], parse_column_identifiers('1,2:4', self.headers, column_offset=0))
        self.assertEqual([4, 2, 5], parse_column_identifiers('more-header-values,3,stuff', self.headers))
        self.assertEqual([4, 3, 5], parse_column_identifiers(
            'more-header-values,3,stuff', self.headers, column_offset=0))

    def test_ignore_unknown_columns(self):
        self.assertEqual(
            [0, 2],
            parse_column_identifiers('id,nope,i_work_here', self.headers, ignore_unknown_columns=True),
        )
        self.assertEqual(
            [],
            parse_column_identifiers('nope,missing', self.headers, ignore_unknown_columns=True),
        )
        # An unknown identifier containing '-' or ':' is skipped too, not parsed as a range.
        self.assertEqual(
            [0, 2],
            parse_column_identifiers('id,no-pe,i_work_here', self.headers, ignore_unknown_columns=True),
        )
        # Without the flag, the same input still raises.
        with self.assertRaises(ColumnIdentifierError):
            parse_column_identifiers('id,no-pe,i_work_here', self.headers)

    def test_exclude_open_ended_range(self):
        # An open-ended exclusion range reaches the last column.
        self.assertEqual(
            [0, 1, 2, 3, 4],
            parse_column_identifiers(None, self.headers, excluded_columns='6-'),
        )

    def test_exclude_ignores_unknown_names_but_reports_invalid_ranges(self):
        # An unknown bare name is skipped (long-standing -C tolerance)...
        self.assertEqual(
            [0, 1, 2, 3, 4, 5, 6],
            parse_column_identifiers(None, self.headers, excluded_columns='nope'),
        )
        # ...but a malformed range is a user error, even for -C.
        with self.assertRaises(ColumnIdentifierError):
            parse_column_identifiers(None, self.headers, excluded_columns='no-pe')
        # ...as is a range that references a nonexistent column.
        with self.assertRaises(ColumnIdentifierError):
            parse_column_identifiers(None, self.headers, excluded_columns='6-99')

    def test_range_notation_open_ended(self):
        self.assertEqual([0, 1, 2], parse_column_identifiers(':3', self.headers))

        target = list(range(3, len(self.headers)))  # protect against devs adding to self.headers
        target.insert(0, 0)
        self.assertEqual(target, parse_column_identifiers('1,4:', self.headers))

        self.assertEqual(list(range(0, len(self.headers))), parse_column_identifiers('1:', self.headers))


class InferenceUtility(CSVKitUtility):
    def add_arguments(self):
        self.add_type_inference_arguments()


class TestInferenceControls(unittest.TestCase):
    def test_default_inference(self):
        utility = CSVSort([])
        table = agate.Table(
            [['001', '10.5', '2026-10-08', 'true']],
            ['identifier', 'amount', 'visit', 'active'], column_types=utility.get_column_types(),
        )
        self.assertEqual(
            tuple(table.rows[0]),
            (decimal.Decimal(1), decimal.Decimal('10.5'), datetime.date(2026, 10, 8), True),
        )

    def test_global_inference_preserves_positional_filename(self):
        for flag in ('-I', '--no-inference'):
            for args in ([flag, 'input.csv'], ['input.csv', flag]):
                with self.subTest(args=args):
                    utility = CSVSort(args)
                    self.assertEqual(utility.args.input_path, 'input.csv')
                    self.assertIs(utility.args.no_inference, True)
                    table = agate.Table([['001', '2']], ['id', 'amount'],
                                        column_types=utility.get_column_types())
                    self.assertEqual(tuple(table.rows[0]), ('001', '2'))


class TestSelectiveInference(unittest.TestCase):
    def get_tester(self, columns, options=()):
        # Supply the new parser destination to the existing shared construction API.
        # This also exercises base policy without depending on new utility registration.
        utility = CSVSort(list(options))
        utility.args.no_inference_columns = columns
        return utility.get_column_types()

    def test_selects_names_indices_and_ranges(self):
        headers = ['identifier', 'amount', 'visit', 'active']
        rows = [['001', '10.5', '2026-10-08', 'true']]
        for columns, options, expected in (
            ('identifier', (), ('001', decimal.Decimal('10.5'), datetime.date(2026, 10, 8), True)),
            ('1,visit', (), ('001', decimal.Decimal('10.5'), '2026-10-08', True)),
            ('1-2', (), ('001', '10.5', datetime.date(2026, 10, 8), True)),
            ('2:3', (), (decimal.Decimal(1), '10.5', '2026-10-08', True)),
            ('0,2', ('--zero',), ('001', decimal.Decimal('10.5'), '2026-10-08', True)),
            ('0-1', ('--zero',), ('001', '10.5', datetime.date(2026, 10, 8), True)),
        ):
            with self.subTest(columns=columns, options=options):
                table = agate.Table(rows, headers, column_types=self.get_tester(columns, options))
                self.assertEqual(tuple(table.rows[0]), expected)

    def test_unicode_header_and_literal_values(self):
        table = agate.Table([['001', 'café 雨', '2']], ['識別子', 'label', 'amount'],
                            column_types=self.get_tester('識別子'))
        self.assertEqual(tuple(table.rows[0]), ('001', 'café 雨', decimal.Decimal(2)))

    def test_default_and_custom_nulls_apply_to_selected_text(self):
        table = agate.Table([['', '2'], ['na', '3'], ['MISSING', '4']], ['id', 'amount'],
                            column_types=self.get_tester('id', ['--null-value', 'MISSING']))
        self.assertEqual(list(table.columns['id']), [None, None, None])
        self.assertIsInstance(table.column_types[1], agate.Number)

    def test_blanks_and_custom_nulls_apply_to_selected_text(self):
        table = agate.Table([['', '2'], ['na', '3'], ['MISSING', '4']], ['id', 'amount'],
                            column_types=self.get_tester('id', ['--blanks', '--null-value', 'MISSING']))
        self.assertEqual(list(table.columns['id']), ['', 'na', None])
        self.assertIsInstance(table.column_types[1], agate.Number)

    def test_locale_and_date_formats_remain_active_for_other_columns(self):
        table = agate.Table(
            [['001', '1.234,50', '08/10/2026', '2026|10|08 15:30']],
            ['id', 'amount', 'day', 'moment'],
            column_types=self.get_tester(
                'id', ['--locale', 'de_DE', '--date-format', '%d/%m/%Y', '--datetime-format', '%Y|%m|%d %H:%M'],
            ),
        )
        self.assertEqual(
            tuple(table.rows[0]),
            ('001', decimal.Decimal('1234.50'), datetime.date(2026, 10, 8), datetime.datetime(2026, 10, 8, 15, 30)),
        )

    def test_no_leading_zeroes_remains_active_for_unselected_column(self):
        table = agate.Table([['001', '10.5']], ['id', 'amount'],
                            column_types=self.get_tester('amount', ['--no-leading-zeroes']))
        self.assertEqual(tuple(table.rows[0]), ('001', '10.5'))

    def test_reused_tester_resolves_each_schema_independently(self):
        for selector in ('1', 'id'):
            with self.subTest(selector=selector):
                tester = self.get_tester(selector)
                first = agate.Table([['001', '2']], ['id', 'amount'], column_types=tester)
                second = agate.Table([['2', '001']], ['amount', 'id'], column_types=tester)
                self.assertEqual(tuple(first.rows[0]), ('001', decimal.Decimal(2)))
                expected = ('2', decimal.Decimal(1)) if selector == '1' else (decimal.Decimal(2), '001')
                self.assertEqual(tuple(second.rows[0]), expected)

    def test_unknown_and_invalid_selectors_raise(self):
        for selector in ('missing', '0', '4', '1-4', '1-nope', '3-1'):
            with self.subTest(selector=selector):
                with self.assertRaises(ColumnIdentifierError):
                    agate.Table([['001', '2']], ['id', 'amount'], column_types=self.get_tester(selector))

    def test_reused_named_selector_does_not_ignore_missing_column(self):
        tester = self.get_tester('id')
        agate.Table([['001', '2']], ['id', 'amount'], column_types=tester)
        with self.assertRaises(ColumnIdentifierError):
            agate.Table([['2', '001']], ['amount', 'other'], column_types=tester)

    def test_empty_header_reports_no_matching_selection(self):
        with self.assertRaises(ColumnIdentifierError):
            self.get_tester('id').run([], [])

    def test_parser_registers_separate_option(self):
        utility = InferenceUtility(['--no-inference-columns', 'id', 'input.csv'])
        self.assertEqual(utility.args.no_inference_columns, 'id')
        self.assertEqual(utility.args.input_path, 'input.csv')
        self.assertIs(utility.args.no_inference, False)

    def test_parser_rejects_empty_selector(self):
        for selector in ('', '   '):
            with self.subTest(selector=selector):
                error = io.StringIO()
                with redirect_stderr(error), self.assertRaises(SystemExit) as raised:
                    InferenceUtility(['--no-inference-columns', selector])
                self.assertEqual(raised.exception.code, 2)
                self.assertIn('must not be empty', error.getvalue())

    def test_parser_rejects_global_and_selected_inference(self):
        for args in (['-I', '--no-inference-columns', 'id'], ['--no-inference-columns', 'id', '--no-inference']):
            with self.subTest(args=args):
                error = io.StringIO()
                with redirect_stderr(error), self.assertRaises(SystemExit) as raised:
                    InferenceUtility(args)
                self.assertEqual(raised.exception.code, 2)
                self.assertIn('not allowed with argument', error.getvalue())
