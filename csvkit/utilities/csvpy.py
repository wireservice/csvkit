#!/usr/bin/env python

import agate

from csvkit.cli import CSVKitUtility


class CSVPy(CSVKitUtility):
    description = 'Load a CSV file into a CSV reader and then drop into a Python shell.'
    override_flags = ['l', 'zero', 'H']

    def add_arguments(self):
        self.argparser.add_argument('--dict', dest='as_dict', action='store_true',
                                    help='Load the CSV file into a DictReader.')
        self.argparser.add_argument('--agate', dest='as_agate', action='store_true',
                                    help='Load the CSV file into an agate table.')

    def main(self):
        # Attempt reading filename, will cause lazy loader to access file and raise error if it does not exist
        filename = self.input_file.name

        if self.args.as_dict:
            klass = agate.csv.DictReader
            class_name = 'agate.csv.DictReader'
            variable_name = 'reader'
        elif self.args.as_agate:
            klass = agate.Table.from_csv
            class_name = 'agate.Table'
            variable_name = 'table'
        else:
            klass = agate.csv.reader
            class_name = 'agate.csv.reader'
            variable_name = 'reader'

        variable = klass(self.input_file, **self.reader_kwargs)

        welcome_message = 'Welcome! "%s" has been loaded in an %s object named "%s".' % (filename, class_name, variable_name)

        try:
            from IPython.frontend.terminal.embed import InteractiveShellEmbed
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
