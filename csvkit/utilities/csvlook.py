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
        
        The expanded format displays each column on its own line with
        the column name on the left and the value on the right, separated
        by a pipe character. This makes it easy to read records with
        many columns without horizontal scrolling.
        
        Args:
            record_num (int): The record number (1-indexed for display)
            column_names (list): List of column names from the table
            row_data (agate.Row): The row data to display
            max_column_width (int, optional): Maximum width for column values
        """
        
        # ====================================================================
        # Record Header Section
        # ====================================================================
        # Print the record header with dashes
        # Format: -[ RECORD N ]-------------------------------------------------
        # This creates a visual separator for each record, making it easy
        # to distinguish between different records in the output.
        # The total length should be 62 characters to match psql's format.
        record_header = f"-[ RECORD {record_num} ]"
        
        # Total width of the separator line
        # This determines how long the dashed line will be
        # We use 62 characters total to match the psql expanded format
        separator_length = 62  # Total width of the separator line
        
        # Calculate how many dashes we need to fill the rest of the line
        # We subtract the length of the header text from the total width
        # The header length varies based on the record number (e.g., "RECORD 1" vs "RECORD 10")
        dashes_needed = separator_length - len(record_header)
        
        # Ensure we have at least some dashes
        # This prevents negative values if the header is somehow longer
        # than the separator length (shouldn't happen, but safety first)
        if dashes_needed < 0:
            dashes_needed = 0
        
        # Print the record separator line
        # This writes the header followed by dashes to create the separator
        # The total line will always be exactly separator_length characters
        self.output_file.write(record_header + ('-' * dashes_needed) + '\n')
        
        # ====================================================================
        # Column Data Section
        # ====================================================================
        # Iterate through each column in the record
        # We use enumerate to get both the index and the column name
        for col_idx, col_name in enumerate(column_names):
            
            # ================================================================
            # Value Extraction
            # ================================================================
            # Get the value for this column from the row
            # The row_data is an agate.Row object that can be indexed
            # by position (col_idx) to get the value for that column
            value = row_data[col_idx]
            
            # ================================================================
            # Value Conversion
            # ================================================================
            # Convert value to string, handling None/null values
            # None values in CSV data should be displayed as empty strings
            # in the expanded view for clarity
            if value is None:
                # Handle None/null values by using an empty string
                value_str = ''
            else:
                # Convert the value to a string representation
                # This works for all Python types (int, float, bool, etc.)
                value_str = str(value)
            
            # ================================================================
            # Value Truncation
            # ================================================================
            # Apply max column width truncation if specified
            # This prevents very long values from making the output
            # difficult to read. We truncate and add ellipsis if needed.
            if max_column_width is not None and len(value_str) > max_column_width:
                # Truncate the string, leaving room for the ellipsis
                # We subtract 3 to account for the "..." we'll add
                value_str = value_str[:max_column_width - 3] + '...'
            
            # ================================================================
            # Formatting
            # ================================================================
            # Format: ColumnName | value
            # We align column names to a fixed width for readability
            # This ensures all the pipe separators line up vertically,
            # making the output much easier to scan visually.
            
            # Calculate the maximum column name width
            # This ensures all column names are aligned to the same width
            # We use a generator expression to find the longest column name
            col_name_width = max(len(name) for name in column_names) if column_names else 0
            
            # Create the formatted line with left-aligned column name
            # The <{col_name_width} format specifier left-aligns the column
            # name within a field of the specified width
            formatted_line = f"{col_name:<{col_name_width}} | {value_str}"
            
            # ================================================================
            # Output
            # ================================================================
            # Write the formatted line to output
            # Each column gets its own line in the expanded format
            self.output_file.write(formatted_line + '\n')

    def _print_expanded_table(self, table, max_rows=None, max_column_width=None):
        """
        Print the entire table in expanded format.
        
        This method iterates through all rows in the table and
        displays each one using the expanded format.
        
        The expanded format is particularly useful for datasets with
        many columns, as it allows users to see all column values for
        a record without needing to scroll horizontally.
        
        Args:
            table (agate.Table): The agate table to display
            max_rows (int, optional): Maximum number of rows to display
            max_column_width (int, optional): Maximum width for column values
        """
        
        # ====================================================================
        # Column Names Extraction
        # ====================================================================
        # Get column names from the table
        # We extract the column names once so we can reuse them for
        # each record. This is more efficient than extracting them
        # repeatedly in the loop.
        column_names = [col.name for col in table.columns]
        
        # ====================================================================
        # Row Count Calculation
        # ====================================================================
        # Determine how many rows to display
        # Start with the total number of rows in the table
        rows_to_display = len(table.rows)
        
        # Apply max_rows limit if specified
        # This allows users to limit the output to a specific number
        # of records, which is useful for previewing large datasets
        if max_rows is not None and max_rows > 0:
            # Use the minimum of the actual row count and the max_rows limit
            # This ensures we don't try to display more rows than exist
            rows_to_display = min(rows_to_display, max_rows)
        
        # ====================================================================
        # Record Iteration and Display
        # ====================================================================
        # Iterate through each row and print it in expanded format
        # We use a range-based loop to have access to the row index
        # for numbering the records
        for row_idx in range(rows_to_display):
            
            # ================================================================
            # Row Extraction
            # ================================================================
            # Get the current row
            # The table.rows attribute is an iterable of agate.Row objects
            # We access rows by index to get the specific row we want
            row = table.rows[row_idx]
            
            # ================================================================
            # Record Printing
            # ================================================================
            # Print this record in expanded format
            # Record numbers are 1-indexed for user-friendly display
            # (users expect record numbers to start at 1, not 0)
            self._print_expanded_record(
                record_num=row_idx + 1,  # 1-indexed for user display
                column_names=column_names,  # Reuse the column names we extracted
                row_data=row,  # The actual row data to display
                max_column_width=max_column_width  # Pass through truncation setting
            )
            
            # ================================================================
            # Record Separator
            # ================================================================
            # Add a blank line between records for readability
            # This makes it easier to visually separate different records
            # when scrolling through the output
            # (except after the last record - no need for trailing blank)
            if row_idx < rows_to_display - 1:
                # Write a blank line to create visual separation
                self.output_file.write('\n')

    def main(self):
        """
        Main execution method for the csvlook utility.
        
        This method handles the core logic of reading the CSV file,
        parsing it into an agate table, and then displaying it in
        either standard table format or expanded format based on
        the command-line arguments.
        
        The method coordinates all the steps needed to process a CSV
        file and display it to the user, including input validation,
        CSV parsing, type inference, and output formatting.
        """
        
        # ====================================================================
        # Input Validation
        # ====================================================================
        # Check if input is expected but not provided
        # This ensures that the user has provided either a file path
        # or piped data via stdin. Without input, we can't do anything.
        if self.additional_input_expected():
            # Raise an error if no input is available
            # This provides a clear error message to the user
            self.argparser.error('You must provide an input file or piped data.')

        # ====================================================================
        # Options Preparation
        # ====================================================================
        # Prepare kwargs dictionary for agate table options
        # This dictionary will be passed to the table printing method
        # to configure various display options
        kwargs = {}
        
        # ====================================================================
        # Precision Handling
        # ====================================================================
        # In agate, max_precision defaults to 3. None means infinity.
        # We need to handle this carefully to preserve user intent.
        # If the user explicitly sets max_precision, we should respect that.
        if self.args.max_precision is not None:
            # Add the max_precision option to our kwargs dictionary
            # This will be passed to the table printing method
            kwargs['max_precision'] = self.args.max_precision

        # ====================================================================
        # Number Ellipsis Configuration
        # ====================================================================
        # Configure number ellipsis behavior if requested
        # When --no-number-ellipsis is specified, we disable the ellipsis
        # that would normally appear when numbers exceed max_precision
        if self.args.no_number_ellipsis:
            # Set the number truncation characters to empty string
            # This disables the ellipsis for numbers
            config.set_option('number_truncation_chars', '')

        # ====================================================================
        # CSV Dialect Detection Configuration
        # ====================================================================
        # Determine sniff limit for CSV dialect detection
        # CSV dialect detection analyzes the file to determine things like
        # delimiter, quote character, etc. The sniff_limit controls how
        # much of the file to analyze.
        # -1 means sniff the entire file, None means use default
        sniff_limit = self.args.sniff_limit if self.args.sniff_limit != -1 else None
        
        # ====================================================================
        # CSV File Reading
        # ====================================================================
        # Read the CSV file into an agate table
        # This handles all the CSV parsing, type inference, etc.
        # The agate library provides robust CSV parsing with automatic
        # type detection and inference capabilities.
        table = agate.Table.from_csv(
            self.input_file,  # The input file (could be stdin or a file path)
            skip_lines=self.args.skip_lines,  # Lines to skip at the start
            sniff_limit=sniff_limit,  # How much to analyze for dialect detection
            row_limit=self.args.max_rows,  # Limit number of rows to read
            column_types=self.get_column_types(),  # Type inference configuration
            line_numbers=self.args.line_numbers,  # Whether to include line numbers
            **self.reader_kwargs,  # Additional reader options (encoding, etc.)
        )

        # ====================================================================
        # Output Format Selection
        # ====================================================================
        # Check if expanded view is requested
        # The expanded view is a new feature that displays records in
        # a psql-like format, which is useful for datasets with many columns
        if self.args.expanded:
            # ================================================================
            # Expanded Format Display
            # ================================================================
            # Display in expanded format (psql-like)
            # This is the new feature for issue #1313
            # The expanded format shows each record with column names
            # on the left and values on the right, one column per line
            self._print_expanded_table(
                table=table,  # The parsed table to display
                max_rows=self.args.max_rows,  # Limit on number of rows
                max_column_width=self.args.max_column_width  # Limit on column width
            )
        else:
            # ================================================================
            # Standard Format Display
            # ================================================================
            # Display in standard table format (default behavior)
            # This is the traditional markdown-compatible table format
            # that csvlook has always used
            table.print_table(
                output=self.output_file,  # Where to write the output
                max_rows=self.args.max_rows,  # Limit on number of rows
                max_columns=self.args.max_columns,  # Limit on number of columns
                max_column_width=self.args.max_column_width,  # Limit on column width
                **kwargs,  # Additional options (like max_precision)
            )


def launch_new_instance():
    """
    Launch a new instance of the CSVLook utility.
    
    This function creates a new CSVLook instance and runs it.
    It's used as the entry point when csvlook is invoked as a
    command-line script.
    """
    
    # Create a new CSVLook utility instance
    # This will parse command-line arguments and set up the utility
    utility = CSVLook()
    
    # Run the utility
    # This will execute the main() method and handle the CSV processing
    utility.run()


# ========================================================================
# Script Entry Point
# ========================================================================
# This block ensures that the script can be run directly from the
# command line. When the script is executed (rather than imported),
# it will launch a new instance of the CSVLook utility.
if __name__ == '__main__':
    # Launch the utility when run as a script
    launch_new_instance()
