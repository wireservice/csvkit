import importlib.metadata
import os
import subprocess
import sysconfig
import tempfile
import unittest


class TestCSVKitCommand(unittest.TestCase):
    def run_command(self, *args):
        executable = os.path.join(sysconfig.get_path('scripts'), 'csvkit' + ('.exe' if os.name == 'nt' else ''))
        self.assertTrue(os.path.isfile(executable), 'Install csvkit before testing its console entry point.')
        with tempfile.TemporaryDirectory() as directory:
            return subprocess.run(
                [executable, *args], cwd=directory, input='', capture_output=True, text=True, timeout=10,
            )

    def test_overview(self):
        package = importlib.metadata.distribution('csvkit')
        commands = sorted(
            entry.name for entry in package.entry_points
            if entry.group == 'console_scripts' and entry.name != 'csvkit'
        )
        self.assertIn('csvcut', commands)
        self.assertIn('in2csv', commands)
        result = self.run_command()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, '')
        self.assertIn(f'csvkit {package.version}', result.stdout)
        listed = [line.strip()[2:] for line in result.stdout.splitlines() if line.strip().startswith('- ')]
        self.assertEqual(listed, commands)
        self.assertIn('csvcut --help', result.stdout)

    def test_help(self):
        overview = self.run_command()
        for flag in ('-h', '--help'):
            with self.subTest(flag=flag):
                result = self.run_command(flag)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout, overview.stdout)
                self.assertEqual(result.stderr, '')

    def test_version(self):
        for flag in ('-V', '--version'):
            with self.subTest(flag=flag):
                result = self.run_command(flag)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout.strip(), f'csvkit {importlib.metadata.version("csvkit")}')
                self.assertEqual(result.stderr, '')

    def test_not_a_subcommand_dispatcher(self):
        result = self.run_command('csvcut')
        self.assertEqual(result.returncode, 2)
        self.assertIn('unrecognized arguments', result.stderr)
