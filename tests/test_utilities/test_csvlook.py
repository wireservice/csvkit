import io
import sys
from unittest.mock import patch

from agate import config

from csvkit.utilities.csvlook import CSVLook, launch_new_instance
from tests.utils import CSVKitTestCase, EmptyFileTests, stdin_as_string


class TestCSVLook(CSVKitTestCase, EmptyFileTests):
    Utility = CSVLook

    def tearDown(self):
        config.set_option('truncation_chars', '…')

    def test_launch_new_instance(self):
        with patch.object(sys, 'argv', [self.Utility.__name__.lower(), 'examples/dummy.csv']):
            launch_new_instance()

    def test_runs(self):
        self.assertLines(['examples/test_utf8.csv'], [
            '| foo | bar | baz |',
            '| --- | --- | --- |',
            '|   1 |   2 | 3   |',
            '|   4 |   5 | ʤ   |',
        ])

    def test_encoding(self):
        self.assertLines(['-e', 'latin1', 'examples/test_latin1.csv'], [
            '| a | b | c |',
            '| - | - | - |',
            '| 1 | 2 | 3 |',
            '| 4 | 5 | © |',
        ])

    def test_simple(self):
        self.assertLines(['examples/dummy3.csv'], [
            '|    a | b | c |',
            '| ---- | - | - |',
            '| True | 2 | 3 |',
            '| True | 4 | 5 |',
        ])

    def test_no_blanks(self):
        self.assertLines(['examples/blanks.csv'], [
            '| a | b | c | d | e | f |',
            '| - | - | - | - | - | - |',
            '|   |   |   |   |   |   |',
        ])

    def test_blanks(self):
        self.assertLines(['--blanks', 'examples/blanks.csv'], [
            '| a | b  | c   | d    | e    | f |',
            '| - | -- | --- | ---- | ---- | - |',
            '|   | NA | N/A | NONE | NULL | . |',
        ])

    def test_no_header_row(self):
        self.assertLines(['--no-header-row', 'examples/no_header_row3.csv'], [
            '| a | b | c |',
            '| - | - | - |',
            '| 1 | 2 | 3 |',
            '| 4 | 5 | 6 |',
        ])

    def test_unicode(self):
        self.assertLines(['examples/test_utf8.csv'], [
            '| foo | bar | baz |',
            '| --- | --- | --- |',
            '|   1 |   2 | 3   |',
            '|   4 |   5 | ʤ   |',
        ])

    def test_unicode_bom(self):
        self.assertLines(['examples/test_utf8_bom.csv'], [
            '| foo | bar | baz |',
            '| --- | --- | --- |',
            '|   1 |   2 | 3   |',
            '|   4 |   5 | ʤ   |',
        ])

    def test_linenumbers(self):
        self.assertLines(['--linenumbers', 'examples/dummy3.csv'], [
            '| line_numbers |    a | b | c |',
            '| ------------ | ---- | - | - |',
            '|            1 | True | 2 | 3 |',
            '|            2 | True | 4 | 5 |',
        ])

    def test_no_inference(self):
        self.assertLines(['--no-inference', 'examples/dummy3.csv'], [
            '| a | b | c |',
            '| - | - | - |',
            '| 1 | 2 | 3 |',
            '| 1 | 4 | 5 |',
        ])

    def test_sniff_limit_no_limit(self):
        self.assertLines(['examples/sniff_limit.csv'], [
            '|    a | b | c |',
            '| ---- | - | - |',
            '| True | 2 | 3 |',
        ])

    def test_sniff_limit_zero_limit(self):
        self.assertLines(['--snifflimit', '0', 'examples/sniff_limit.csv'], [
            '| a;b;c |',
            '| ----- |',
            '| 1;2;3 |',
        ])

    def test_max_rows(self):
        self.assertLines(['--max-rows', '0', 'examples/dummy.csv'], [
            '| a | b | c |',
            '| - | - | - |',
        ])

    def test_max_columns(self):
        self.assertLines(['--max-columns', '1', 'examples/dummy.csv'], [
            '|    a | ... |',
            '| ---- | --- |',
            '| True | ... |',
        ])

    def test_max_column_width(self):
        self.assertLines(['--max-column-width', '1', 'examples/dummy.csv'], [
            '|     a | b | c |',
            '| ----- | - | - |',
            '| Tr... | 2 | 3 |',
        ])

    def test_max_precision(self):
        self.assertLines(['--max-precision', '0', 'examples/test_precision.csv'], [
            '|  a |',
            '| -- |',
            '| 1… |',
        ])

    def test_no_number_ellipsis(self):
        self.assertLines(['--no-number-ellipsis', 'examples/test_precision.csv'], [
            '|     a |',
            '| ----- |',
            '| 1.235 |',
        ])

    def test_max_precision_no_number_ellipsis(self):
        self.assertLines(['--max-precision', '0', '--no-number-ellipsis', 'examples/test_precision.csv'], [
            '| a |',
            '| - |',
            '| 1 |',
        ])

    def test_stdin(self):
        input_file = io.BytesIO(b'a,b,c\n1,2,3\n4,5,6\n')

        with stdin_as_string(input_file):
            self.assertLines([], [
                '| a | b | c |',
                '| - | - | - |',
                '| 1 | 2 | 3 |',
                '| 4 | 5 | 6 |',
            ])

        input_file.close()


class TestNonSeekableInput(CSVKitTestCase):
    Utility = CSVLook

    def _run_on_fifo(self, options):
        import os
        import subprocess
        import sys
        import tempfile
        import time

        with tempfile.TemporaryDirectory() as tmpdir:
            fifo = os.path.join(tmpdir, 'pipe.csv')
            os.mkfifo(fifo)

            process = subprocess.Popen(
                [sys.executable, '-m', 'csvkit.utilities.csvlook'] + options + [fifo],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            # Open the write end only after the utility has opened the read
            # end, as opening a FIFO blocks until the other end is open.
            deadline = time.time() + 30
            while True:
                try:
                    writer = os.open(fifo, os.O_WRONLY | os.O_NONBLOCK)
                    break
                except OSError:
                    if time.time() > deadline or process.poll() is not None:
                        process.kill()
                        raise
                    time.sleep(0.05)

            os.write(writer, b'a,b\n1,2\n3,4\n')
            os.close(writer)

            return process.communicate(timeout=30)

    def test_unseekable_input_suggests_snifflimit_zero(self):
        import os
        import unittest

        if not hasattr(os, 'mkfifo'):
            raise unittest.SkipTest('requires os.mkfifo')

        _stdout, stderr = self._run_on_fifo([])

        self.assertIn('--snifflimit 0', stderr.decode('utf-8'))

    def test_snifflimit_zero_reads_unseekable_input(self):
        import os
        import unittest

        if not hasattr(os, 'mkfifo'):
            raise unittest.SkipTest('requires os.mkfifo')

        stdout, _stderr = self._run_on_fifo(['--snifflimit', '0'])

        self.assertIn('| a | b |', stdout.decode('utf-8'))
        self.assertIn('| 1 | 2 |', stdout.decode('utf-8'))
