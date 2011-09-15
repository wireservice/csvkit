#!/usr/bin/env python

from os.path import splitext

from csvkit import CSVKitReader, CSVKitWriter
from csvkit.cli import CSVKitUtility 
from csvkit.cleanup import RowChecker

class CSVClean(CSVKitUtility):
    description = 'Fix errors in a CSV file.'

    def add_arguments(self):
        self.argparser.add_argument('-n', '--dry-run', dest='dryrun', action='store_true',
                                    help='If this argument is present, no output will be created. Information about what would have been done will be printed to STDERR.''')

    def main(self):
        reader = CSVKitReader(self.args.file, **self.reader_kwargs)

        if self.args.dryrun:
            checker = RowChecker(reader)
            for row in checker.checked_rows():
                pass
            if checker.errs:
                for e in checker.errs:
                    self.output_file.write("Line %i: %s\n" % (e.line_number,e.msg))
            else:
                self.output_file.write("No errors.\n")
            if checker.joins:
                self.output_file.write("%i rows would have been joined/reduced to %i rows after eliminating expected internal line breaks.\n" % (checker.rows_joined, checker.joins))
        else:
            base,ext = splitext(self.args.file.name)
            # should we preserve delimiters and other dialect args from CLI?
            cleaned_file = CSVKitWriter(open("%s_out.csv" % base,"w"), **self.writer_kwargs)

            checker = RowChecker(reader)
            cleaned_file.writerow(checker.column_names)
            for row in checker.checked_rows():
                cleaned_file.writerow(row)
            
            if checker.errs:
                # should we preserve delimiters and other dialect args from CLI?
                err_filename = "%s_err.csv" % base
                err_file = CSVKitWriter(open(err_filename, "w"), **self.writer_kwargs)
                err_header = ['line_number','msg']
                err_header.extend(checker.column_names)
                err_file.writerow(err_header)
                for e in checker.errs:
                    err_file.writerow(self._format_error_row(e))
                    err_count = len(checker.errs)
                self.output_file.write("%i error%s logged to %s\n" % (err_count,"" if err_count == 1 else "s", err_filename))
            else:
                self.output_file.write("No errors.\n")

            if checker.joins:
                self.output_file.write("%i rows were joined/reduced to %i rows after eliminating expected internal line breaks.\n" % (checker.rows_joined, checker.joins))

    def _format_error_row(self, e):
        """Format a row for """
        err_row = [e.line_number, e.msg]
        err_row.extend(e.row)
        return err_row

if __name__ == '__main__':
    utility = CSVClean()
    utility.main()
