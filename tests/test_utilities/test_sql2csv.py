import io
import os
import sys
import tempfile
from unittest.mock import patch

try:
    import psycopg2  # noqa: F401
    postgresql_scheme = 'postgresql'
except ImportError:
    # http://docs.sqlalchemy.org/en/latest/dialects/postgresql.html#module-sqlalchemy.dialects.postgresql.psycopg2cffi
    postgresql_scheme = 'postgresql+psycopg2cffi'

from csvkit.utilities.csvsql import CSVSQL
from csvkit.utilities.sql2csv import SQL2CSV, launch_new_instance
from tests.utils import CSVKitTestCase, EmptyFileTests, stdin_as_string


class TestSQL2CSV(CSVKitTestCase, EmptyFileTests):
    Utility = SQL2CSV

    def test_launch_new_instance(self):
        with patch.object(sys, 'argv', [self.Utility.__name__.lower(), '--query', 'select 1']):
            launch_new_instance()

    def setUp(self):
        self.db_file = 'foo.db'

    def tearDown(self):
        try:
            os.remove(self.db_file)
        except OSError:
            pass

    def csvsql(self, csv_file, db=None):
        """
        Load test data into the DB and return it as a string for comparison.
        """
        if not db:
            db = 'sqlite:///' + self.db_file

        args = ['--db', db, '--tables', 'foo', '--insert', csv_file, '--no-inference']

        utility = CSVSQL(args)
        utility.run()

        with open(csv_file) as f:
            text = f.read()

        return text.strip()

    def test_encoding(self):
        # Test that csvstat doesn't error on Latin-1 input.
        self.get_output(['-e', 'latin1', 'examples/test.sql'])

    def test_query(self):
        csv = self.get_output(['--query', 'select 6*9 as question'])

        self.assertTrue('question' in csv)
        self.assertTrue('54' in csv)

    def test_bind_parameter_value(self):
        self.assertRows(
            ['--query', 'select :value as value', '--parameter', 'value', "O'Reilly"],
            [['value'], ["O'Reilly"]],
        )

    def test_bind_parameters_multiple(self):
        self.assertRows(
            ['--query', 'select cast(:a as integer) + cast(:b as integer) as total',
             '-b', 'a', '3', '-b', 'b', '5'],
            [['total'], ['8']],
        )

    def test_bind_parameters_preserve_strings(self):
        self.assertRows(
            ['--query', 'select :code as code, :word as word',
             '--parameter', 'code', '00123', '--parameter', 'word', 'None'],
            [['code', 'word'], ['00123', 'None']],
        )

    def test_bind_parameters_are_not_sql(self):
        self.assertRows(
            ['--query', "with names(name) as (values ('alice'), ('bob')) "
                        'select count(*) as matches from names where name = :name',
             '--parameter', 'name', "alice' OR 1=1 --"],
            [['matches'], ['0']],
        )

    def test_bind_parameters_in_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, 'query.sql')
            with open(path, 'w', encoding='utf-8') as f:
                f.write('select :value as value')
            self.assertRows([path, '--parameter', 'value', 'from file'], [['value'], ['from file']])

    def test_bind_parameters_in_stdin(self):
        with stdin_as_string(io.BytesIO(b'select :value as value')):
            self.assertRows(['--parameter', 'value', 'from stdin'], [['value'], ['from stdin']])

    def test_bind_parameters_unicode_and_csv_quoting(self):
        value = 'Привет, "CSV"\nnext line'
        self.assertRows(
            ['--query', 'select :value as value', '--parameter', 'value', value], [['value'], [value]],
        )

    def test_bind_parameters_repeated_name(self):
        self.assertRows(
            ['--query', 'select :value as value', '-b', 'value', 'first', '-b', 'value', 'last'],
            [['value'], ['last']],
        )

    def test_bind_parameters_no_header_row(self):
        self.assertRows(['--query', 'select :value as value', '--no-header-row', '-b', 'value', 'a'], [['a']])

    def test_bind_parameters_filter_table(self):
        self.csvsql('examples/dummy.csv')
        self.assertRows(
            ['--db', 'sqlite:///' + self.db_file, '--query', 'select a, b from foo where a = :value',
             '--parameter', 'value', '1'],
            [['a', 'b'], ['1', '2']],
        )

    def test_query_without_bind_parameters_keeps_driver_sql(self):
        self.assertRows(['--query', "select ':not_a_parameter' as value, '100%' as percent"],
                        [['value', 'percent'], [':not_a_parameter', '100%']])

    def test_bind_parameter_missing_value(self):
        self.assertError(launch_new_instance, ['--parameter', 'value'],
                         'argument -b/--parameter: expected 2 arguments', args=[])

    def test_file(self):
        csv = self.get_output(['examples/test.sql'])

        self.assertTrue('question' in csv)
        self.assertTrue('36' in csv)

    def test_file_with_query(self):
        csv = self.get_output(['examples/test.sql', '--query', 'select 6*9 as question'])

        self.assertTrue('question' in csv)
        self.assertTrue('54' in csv)

    def test_stdin(self):
        input_file = io.BytesIO(b'select cast(3.1415 * 13.37 as integer) as answer')

        with stdin_as_string(input_file):
            csv = self.get_output([])

            self.assertTrue('answer' in csv)
            self.assertTrue('42' in csv)

        input_file.close()

    def test_stdin_with_query(self):
        input_file = io.BytesIO(b'select cast(3.1415 * 13.37 as integer) as answer')

        with stdin_as_string(input_file):
            csv = self.get_output(['--query', 'select 6*9 as question'])

            self.assertTrue('question' in csv)
            self.assertTrue('54' in csv)

        input_file.close()

    def test_stdin_with_file(self):
        input_file = io.BytesIO(b'select cast(3.1415 * 13.37 as integer) as answer')

        with stdin_as_string(input_file):
            csv = self.get_output(['examples/test.sql'])

            self.assertTrue('question' in csv)
            self.assertTrue('36' in csv)

        input_file.close()

    def test_stdin_with_file_and_query(self):
        input_file = io.BytesIO(b'select cast(3.1415 * 13.37 as integer) as answer')

        with stdin_as_string(input_file):
            csv = self.get_output(['examples/test.sql', '--query', 'select 6*9 as question'])

            self.assertTrue('question' in csv)
            self.assertTrue('54' in csv)

        input_file.close()

    def test_unicode(self):
        expected = self.csvsql('examples/test_utf8.csv')
        csv = self.get_output(['--db', 'sqlite:///' + self.db_file, '--query', 'select * from foo'])
        self.assertEqual(csv.strip(), expected)

    def test_no_header_row(self):
        self.csvsql('examples/dummy.csv')
        csv = self.get_output(['--db', 'sqlite:///' + self.db_file, '--no-header-row', '--query', 'select * from foo'])

        self.assertTrue('a,b,c' not in csv)
        self.assertTrue('1,2,3' in csv)

    def test_linenumbers(self):
        self.csvsql('examples/dummy.csv')
        csv = self.get_output(['--db', 'sqlite:///' + self.db_file, '--linenumbers', '--query', 'select * from foo'])

        self.assertTrue('line_number,a,b,c' in csv)
        self.assertTrue('1,1,2,3' in csv)

    def test_wildcard_on_sqlite(self):
        self.csvsql('examples/iris.csv')
        csv = self.get_output(['--db', 'sqlite:///' + self.db_file, '--query',
                              "select * from foo where species LIKE '%'"])

        self.assertTrue('sepal_length,sepal_width,petal_length,petal_width,species' in csv)
        self.assertTrue('5.1,3.5,1.4,0.2,Iris-setosa' in csv)

    # def test_wildcard_on_postgresql(self):
    #     db = postgresql_scheme + ':///dummy_test'

    #     self.csvsql('examples/iris.csv', db)
    #     csv = self.get_output(['--db', db, '--query', "select * from foo where species LIKE '%'"])

    #     self.assertTrue('sepal_length,sepal_width,petal_length,petal_width,species' in csv)
    #     self.assertTrue('5.1,3.5,1.4,0.2,Iris-setosa' in csv)
