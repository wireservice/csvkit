import warnings


class NullCalculationWarning(RuntimeWarning):  # pragma: no cover
    """
    Warning raised if a calculation which can not logically
    account for null values is performed on a :class:`.Column` containing
    nulls.
    """
    pass


def warn_null_calculation(operation, column):
    warnings.warn('Column "{}" contains nulls. These will be excluded from {} calculation.'.format(
        column.name,
        operation.__class__.__name__
    ), NullCalculationWarning, stacklevel=2)


class DuplicateColumnWarning(RuntimeWarning):  # pragma: no cover
    """
    Warning raised if multiple columns with the same name are added to a new
    :class:`.Table`.
    """
    pass


def warn_duplicate_column(column_name, column_rename):
    warnings.warn('Column name "{}" already exists in Table. Column will be renamed to "{}".'.format(
        column_name,
        column_rename
    ), DuplicateColumnWarning, stacklevel=2)


class UnnamedColumnWarning(RuntimeWarning):  # pragma: no cover
    """
    Warning raised when a column has no name and an a programmatically generated
    name is used.
    """
    pass


def warn_unnamed_column(column_id, new_column_name):
    warnings.warn('Column %i has no name. Using "%s".' % (
        column_id,
        new_column_name
    ), UnnamedColumnWarning, stacklevel=2)
