import unittest

import agate


class AgateTestCase(unittest.TestCase):
    """
    Unittest case for quickly asserting logic about tables.
    """
    def assertColumnNames(self, table, names):
        """
        Verify the column names in the given table match what is expected.
        """
        self.assertIsInstance(table, agate.Table)

        self.assertSequenceEqual(table.column_names, names)
        self.assertSequenceEqual(
            [c.name for c in table.columns],
            names
        )

        for row in table.rows:
            self.assertSequenceEqual(
                row.keys(),
                names
            )

    def assertColumnTypes(self, table, types):
        """
        Verify the column types in the given table are of the expected types.
        """
        self.assertIsInstance(table, agate.Table)

        table_types = table.column_types
        column_types = [c.data_type for c in table.columns]

        for i, test_type in enumerate(types):
            self.assertIsInstance(table_types[i], test_type)
            self.assertIsInstance(column_types[i], test_type)

    def assertRows(self, table, rows):
        """
        Verify the row data in the given table match what is expected.
        """
        self.assertIsInstance(table, agate.Table)

        for i, row in enumerate(rows):
            self.assertSequenceEqual(table.rows[i], row)

    def assertRowNames(self, table, names):
        """
        Verify the row names in the given table match what is expected.
        """
        self.assertIsInstance(table, agate.Table)

        self.assertSequenceEqual(table.row_names, names)
        self.assertSequenceEqual(
            table.rows.keys(),
            names
        )

        for column in table.columns:
            self.assertSequenceEqual(
                column.keys(),
                names
            )
