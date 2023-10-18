import io
import os
import sys
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
