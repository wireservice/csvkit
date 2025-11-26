#!/usr/bin/env python

# This module implements the csvlook utility, which renders CSV files
# in a human-readable format in the terminal.
#
# The main feature is the standard table view, but we also support
# an "expanded" view similar to psql's expanded display mode, where
# each record is displayed with column names on the left and values
# on the right, one column per line.

import agate
from agate import config

from csvkit.cli import CSVKitUtility


class CSVLook(CSVKitUtility):
    """
    CSVLook utility class that provides table rendering functionality.
    
    This class extends CSVKitUtility and provides methods to display
    CSV data in either standard table format or expanded format.
    
    The expanded format is similar to psql's expanded view, displaying
    each record with column names on the left and values on the right,
    which is useful for exploring datasets with many columns.
    """
    
    description = 'Render a CSV file in the console as a Markdown-compatible, fixed-width table.'

    def add_arguments(self):
        """
        Add command-line arguments for the csvlook utility.
        
        This method defines all the optional arguments that can be
        passed to the csvlook command, including display options
        and CSV parsing options.
        """
        
        # Maximum rows argument - limits how many rows to display
        self.argparser.add_argument(
            '--max-rows', dest='max_rows', type=int,
            help='The maximum number of rows to display before truncating the data.')
        
        # Maximum columns argument - limits how many columns to display
        self.argparser.add_argument(
            '--max-columns', dest='max_columns', type=int,
            help='The maximum number of columns to display before truncating the data.')
        
        # Maximum column width argument - truncates long column values
        self.argparser.add_argument(
            '--max-column-width', dest='max_column_width', type=int,
            help='Truncate all columns to at most this width. The remainder will be replaced with ellipsis.')
        
        # Maximum precision argument - controls decimal places
        self.argparser.add_argument(
            '--max-precision', dest='max_precision', type=int,
            help='The maximum number of decimal places to display. The remainder will be replaced with ellipsis.')
        
        # Number ellipsis control argument
        self.argparser.add_argument(
            '--no-number-ellipsis', dest='no_number_ellipsis', action='store_true',
            help='Disable the ellipsis if --max-precision is exceeded.')
        
        # Sniff limit argument - controls CSV dialect detection
        self.argparser.add_argument(
            '-y', '--snifflimit', dest='sniff_limit', type=int, default=1024,
            help='Limit CSV dialect sniffing to the specified number of bytes. '
                 'Specify "0" to disable sniffing entirely, or "-1" to sniff the entire file.')
        
        # Type inference control argument
        self.argparser.add_argument(
            '-I', '--no-inference', dest='no_inference', action='store_true',
            help='Disable type inference (and --locale, --date-format, --datetime-format, --no-leading-zeroes) '
                 'when parsing the input.')
        
        # Expanded view argument - enables psql-like expanded display
        # This is the new feature requested in issue #1313
        self.argparser.add_argument(
            '--expanded', dest='expanded', action='store_true',
            help='Display records in expanded format (like psql). Each record is displayed '
                 'with column names on the left and values on the right, one column per line. '
                 'Useful for exploring datasets with many columns.')

    def _print_expanded_record(self, record_num, column_names, row_data, max_column_width=None):
        """
        Print a single record in expanded format.
        
        This method formats and prints one record from the CSV table
        in the expanded format, similar to psql's expanded display.
        
        Args:
            record_num (int): The record number (1-indexed for display)
            column_names (list): List of column names from the table
            row_data (agate.Row): The row data to display
            max_column_width (int, optional): Maximum width for column values
        """
        
        # Print the record header with dashes
        # Format: -[ RECORD N ]-------------------------------------------------
        record_header = f"-[ RECORD {record_num} ]"
        separator_length = 60  # Total width of the separator line
        dashes_needed = separator_length - len(record_header)
        
        # Ensure we have at least some dashes
        if dashes_needed < 0:
            dashes_needed = 0
        
        # Print the record separator line
        self.output_file.write(record_header + ('-' * dashes_needed) + '\n')
        
        # Iterate through each column in the record
        for col_idx, col_name in enumerate(column_names):
            
            # Get the value for this column from the row
            value = row_data[col_idx]
            
            # Convert value to string, handling None/null values
            if value is None:
                value_str = ''
            else:
                value_str = str(value)
            
            # Apply max column width truncation if specified
            if max_column_width is not None and len(value_str) > max_column_width:
                value_str = value_str[:max_column_width - 3] + '...'
            
            # Format: ColumnName | value
            # We align column names to a fixed width for readability
            col_name_width = max(len(name) for name in column_names) if column_names else 0
            formatted_line = f"{col_name:<{col_name_width}} | {value_str}"
            
            # Write the formatted line to output
            self.output_file.write(formatted_line + '\n')

    def _print_expanded_table(self, table, max_rows=None, max_column_width=None):
        """
        Print the entire table in expanded format.
        
        This method iterates through all rows in the table and
        displays each one using the expanded format.
        
        Args:
            table (agate.Table): The agate table to display
            max_rows (int, optional): Maximum number of rows to display
            max_column_width (int, optional): Maximum width for column values
        """
        
        # Get column names from the table
        column_names = [col.name for col in table.columns]
        
        # Determine how many rows to display
        rows_to_display = len(table.rows)
        if max_rows is not None and max_rows > 0:
            rows_to_display = min(rows_to_display, max_rows)
        
        # Iterate through each row and print it in expanded format
        for row_idx in range(rows_to_display):
            
            # Get the current row
            row = table.rows[row_idx]
            
            # Print this record in expanded format
            # Record numbers are 1-indexed for user-friendly display
            self._print_expanded_record(
                record_num=row_idx + 1,
                column_names=column_names,
                row_data=row,
                max_column_width=max_column_width
            )
            
            # Add a blank line between records for readability
            # (except after the last record)
            if row_idx < rows_to_display - 1:
                self.output_file.write('\n')

    def main(self):
        """
        Main execution method for the csvlook utility.
        
        This method handles the core logic of reading the CSV file,
        parsing it into an agate table, and then displaying it in
        either standard table format or expanded format based on
        the command-line arguments.
        """
        
        # Check if input is expected but not provided
        if self.additional_input_expected():
            self.argparser.error('You must provide an input file or piped data.')

        # Prepare kwargs dictionary for agate table options
        kwargs = {}
        
        # In agate, max_precision defaults to 3. None means infinity.
        # We need to handle this carefully to preserve user intent.
        if self.args.max_precision is not None:
            kwargs['max_precision'] = self.args.max_precision

        # Configure number ellipsis behavior if requested
        if self.args.no_number_ellipsis:
            config.set_option('number_truncation_chars', '')

        # Determine sniff limit for CSV dialect detection
        # -1 means sniff the entire file, None means use default
        sniff_limit = self.args.sniff_limit if self.args.sniff_limit != -1 else None
        
        # Read the CSV file into an agate table
        # This handles all the CSV parsing, type inference, etc.
        table = agate.Table.from_csv(
            self.input_file,
            skip_lines=self.args.skip_lines,
            sniff_limit=sniff_limit,
            row_limit=self.args.max_rows,
            column_types=self.get_column_types(),
            line_numbers=self.args.line_numbers,
            **self.reader_kwargs,
        )

        # Check if expanded view is requested
        if self.args.expanded:
            # Display in expanded format (psql-like)
            # This is the new feature for issue #1313
            self._print_expanded_table(
                table=table,
                max_rows=self.args.max_rows,
                max_column_width=self.args.max_column_width
            )
        else:
            # Display in standard table format (default behavior)
            table.print_table(
                output=self.output_file,
                max_rows=self.args.max_rows,
                max_columns=self.args.max_columns,
                max_column_width=self.args.max_column_width,
                **kwargs,
            )


def launch_new_instance():
    utility = CSVLook()
    utility.run()


if __name__ == '__main__':
    launch_new_instance()
