#!/usr/bin/env python

import os

from csvkit import CSVKitReader
from csvkit.cli import CSVKitUtility 

class CSVLook(CSVKitUtility):
    description = 'Load a CSV file into a CSVKitReader object and then drops into a Python shell.'
    override_flags = 'l'

    welcome_message = 'Welcome! Your data has been loaded in a CSVKitReader object named "reader".'

    def add_arguments(self):
        pass

    def main(self):
        reader = CSVKitReader(self.args.file, **self.reader_kwargs)

        try:
            from IPython.frontend.terminal.embed import InteractiveShellEmbed
            ipy = InteractiveShellEmbed(banner1=self.welcome_message)
            ipy()
        except ImportError:
            import code
            code.interact(self.welcome_message, local={ 'reader': reader })        

def launch_new_instance():
    utility = CSVLook()
    utility.main()
    
if __name__ == "__main__":
    launch_new_instance()

