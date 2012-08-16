#!/usr/bin/env python

from csvkit import CSVKitReader
from csvkit.cli import CSVKitUtility 

class CSVLook(CSVKitUtility):
    description = 'Render a CSV file in the console as a fixed-width table.'
    override_flags = 'l'

    def add_arguments(self):
        pass

    def main(self):
        rows = CSVKitReader(self.args.file, **self.reader_kwargs)
        rows = list(rows)

        widths = []

        for row in rows:
            for i, v in enumerate(row):
                try:
                    if len(v) > widths[i]:
                        widths[i] = len(v)
                except IndexError:
                    widths.append(len(v))

        # Dashes span each width with '+' character at intersection of
        # horizontal and vertical dividers.
        divider = '|--' + '-+-'.join('-'* w for w in widths) + '--|'

        self.output_file.write('%s\n' % divider)

        for i, row in enumerate(rows):
            output = []

            for j, d in enumerate(row):
                if d is None:
                    d = ''
                output.append(' %s ' % unicode(d).ljust(widths[j]))

            self.output_file.write(('| %s |\n' % ('|'.join(output))).encode('utf-8'))

            if i == 0 or i == len(rows) - 1:
                self.output_file.write('%s\n' % divider)

def launch_new_instance():
    utility = CSVLook()
    utility.main()
    
if __name__ == "__main__":
    launch_new_instance()

