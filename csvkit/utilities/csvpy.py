#!/usr/bin/env python

import sys

import agate
from agate import config

from csvkit.cli import CSVKitUtility


class CSVPy(CSVKitUtility):
    description = 'Load a CSV file into a CSV reader and then drop into a Python shell.'
    override_flags = ['l', 'zero']

    def add_arguments(self):
        self.argparser.add_argument(
            '--dict', dest='as_dict', action='store_true',
            help='Load the CSV file into a DictReader.')
        self.argparser.add_argument(
            '--agate', dest='as_agate', action='store_true',
            help='Load the CSV file into an agate table.')
        self.argparser.add_argument(
            '--no-number-ellipsis', dest='no_number_ellipsis', action='store_true',
            help='Disable the ellipsis if the max precision is exceeded.')
        self.argparser.add_argument(
            '-y', '--snifflimit', dest='sniff_limit', type=int, default=1024,
            help='Limit CSV dialect sniffing to the specified number of bytes. '
                 'Specify "0" to disable sniffing entirely, or "-1" to sniff the entire file.')
        self.argparser.add_argument(
            '-I', '--no-inference', dest='no_inference', action='store_true',
            help='Disable type inference when parsing the input. This disables the reformatting of values.')

    def main(self):
        if self.input_file == sys.stdin:
            self.argparser.error('csvpy cannot accept input as piped data via STDIN.')

        if self.args.no_number_ellipsis:
            config.set_option('number_truncation_chars', '')

        # Attempt reading filename, will cause lazy loader to access file and raise error if it does not exist
        filename = self.input_file.name

        if self.args.as_dict:
            klass = agate.csv.DictReader
            class_name = 'agate.csv.DictReader'
            variable_name = 'reader'
            input_file = self.skip_lines()
            kwargs = {}
        elif self.args.as_agate:
            klass = agate.Table.from_csv
            class_name = 'agate.Table'
            variable_name = 'table'
            input_file = self.input_file

            sniff_limit = self.args.sniff_limit if self.args.sniff_limit != -1 else None
            kwargs = dict(
                skip_lines=self.args.skip_lines,
                sniff_limit=sniff_limit,
                column_types=self.get_column_types(),
            )
        else:
            klass = agate.csv.reader
            class_name = 'agate.csv.reader'
            variable_name = 'reader'
            input_file = self.skip_lines()
            kwargs = {}

        variable = klass(input_file, **kwargs, **self.reader_kwargs)

        welcome_message = f'Welcome! "{filename}" has been loaded in an {class_name} object named "{variable_name}".'

        try:
            from IPython.frontend.terminal.embed import InteractiveShellEmbed
            exec(f'{variable_name} = variable')
            ipy = InteractiveShellEmbed(banner1=welcome_message)
            ipy()
        except ImportError:
            import code
            code.interact(welcome_message, local={variable_name: variable})


def launch_new_instance():
    utility = CSVPy()
    utility.run()


if __name__ == '__main__':
    launch_new_instance()
