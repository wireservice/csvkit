#!/usr/bin/env python

import sys

from csvkit import CSVKitReader
from csvkit.cli import CSVKitUtility 

class CSVPy(CSVKitUtility):
    description = 'Load a CSV file into a CSVKitReader object and then drops into a Python shell.'
    override_flags = 'l'

    welcome_message = 'Welcome! Your data has been loaded in a CSVKitReader object named "reader".'

    def add_arguments(self):
        pass

    def main(self):
        if self.args.file == sys.stdin:
            raise NotImplementedError('csvpy does not currently support input via pipes. Sorry!')
        else:
            # Attempt reading filename, will cause lazy loader to access file and raise error if it does not exist
            filename = self.args.file.name

        reader = CSVKitReader(self.args.file, **self.reader_kwargs)

        try:
            from IPython.frontend.terminal.embed import InteractiveShellEmbed
            ipy = InteractiveShellEmbed(banner1=self.welcome_message)
            ipy()
        except ImportError:
            import code
            code.interact(self.welcome_message, local={ 'reader': reader })        

def launch_new_instance():
    utility = CSVPy()
    utility.main()
    
if __name__ == "__main__":
    launch_new_instance()

