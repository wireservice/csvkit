#!/usr/bin/env python

from csvkit import table

class JoinError(Exception):
    """
    Exception raised when there is a problem joing tables.
    """
    def __init__(self, msg):
        self.msg = msg

def _get_join_column(tab, name):
    """
    Get the column that should be used for making the join. 
    """
    try:
        index = tab.headers().index(name)
    except ValueError:
        raise JoinError('Table does not have a column named "%s"' % name)

    as_set = set(tab[index])

    if len(tab[index]) != len(as_set):
        raise JoinError('Table\'s column named "%s" contains duplicate values')

    return index, tab[index], as_set

def _clone_columns_empty(tab):
    """
    Creates an array of columns that duplicate those in an existing table, but have no data.
    """
    columns = []

    for c in tab:
        n = table.Column(0, c.name, [], normal_type=c.type)
        n.nullable = c.nullable
        n.max_length = c.max_length

        columns.append(n)

    return columns

def inner_join(left_table, left_column_name, right_table, right_column_name):
    """
    Execute an inner join on two tables and return the combined table.
    """
    jointab = table.Table()
    
    # Get the columns which will function as keys 
    left_join_index, left_join_column, left_as_set = _get_join_column(left_table, left_column_name)
    right_join_index, right_join_column, right_as_set = _get_join_column(right_table, right_column_name)

    # Inner join = interesection
    joined_keys = sorted(list(left_as_set.intersection(right_as_set)))

    # Create new columns to hold outputs from both tables 
    columns_from_left = _clone_columns_empty(left_table)
    columns_from_right = _clone_columns_empty(right_table)

    # Iterate over joined keys, adding column values from both tables
    for v in joined_keys:
        i = left_join_column.index(v)

        for j, c in enumerate(left_table):
            columns_from_left[j].append(c[i])

        i = right_join_column.index(v)

        for j, c in enumerate(right_table):
            columns_from_right[j].append(c[i])

    # Drop duplicate key column
    del columns_from_right[right_join_index]

    # Build table from newly truncated columns
    jointab.extend(columns_from_left)
    jointab.extend(columns_from_right)

    # Compute nullable and max_length properties for joined columns 
    for c in jointab:
        c._compute_nullable()
        c._compute_max_length()

    return jointab

def full_outer_join(left_table, left_column_name, right_table, right_column_name):
    """
    Execute full outer join on two tables and return the combined table.
    """
    jointab = table.Table()
    
    # Get the columns which will function as keys 
    left_join_index, left_join_column, left_as_set = _get_join_column(left_table, left_column_name)
    right_join_index, right_join_column, right_as_set = _get_join_column(right_table, right_column_name)
    
    # Full outer join = union
    joined_keys = sorted(list(left_as_set.union(right_as_set)))
    
    # Create a column to hold key values
    key_column = table.Column(0, left_join_column.name, [], normal_type=left_join_column.type)
    key_column.nullable = left_join_column.nullable
    key_column.max_length = left_join_column.max_length

    # Create new columns to hold outputs from both tables 
    columns_from_left = _clone_columns_empty(left_table)
    columns_from_right = _clone_columns_empty(right_table)

    # Iterate over joined keys, adding column values from both tables
    for v in joined_keys:
        key_column.append(v)

        try:
            i = left_join_column.index(v)

            for j, c in enumerate(left_table):
                columns_from_left[j].append(c[i])
        except:
            for j, c in enumerate(left_table):
                columns_from_left[j].append(None)

        try:
            i = right_join_column.index(v)

            for j, c in enumerate(right_table):
                columns_from_right[j].append(c[i])
        except:
            for j, c in enumerate(right_table):
                columns_from_right[j].append(None)

    # Drop key columns
    del columns_from_left[left_join_index]
    del columns_from_right[right_join_index]

    # Build table from newly truncated columns
    jointab.append(key_column)
    jointab.extend(columns_from_left)
    jointab.extend(columns_from_right)

    # Compute nullable and max_length properties for joined columns 
    for c in jointab:
        c._compute_nullable()
        c._compute_max_length()

    return jointab

def left_outer_join(left_table, left_column_name, right_table, right_column_name):
    raise NotImplementedError()

def right_outer_join(left_table, left_column_name, right_table, right_column_name):
    raise NotImplementedError()
