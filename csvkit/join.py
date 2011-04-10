#!/usr/bin/env python

from csvkit import table

class JoinError(Exception):
    """
    Exception raised when there is a problem joing tables.
    """
    def __init__(self, msg):
        self.msg = msg

def _get_join_column(tab, name):
    try:
        index = tab.headers().index(name)
    except ValueError:
        raise JoinError('Table does not have a column named "%s"' % name)

    if len(tab[index]) != len(set(tab[index])):
        raise JoinError('Table\'s column named "%s" contains duplicate values')

    return index, tab[index]

def inner_join(left_table, left_column_name, right_table, right_column_name):
    jointab = table.Table()
    
    # Get the columns which will function as ids
    left_join_index, left_join_column = _get_join_column(left_table, left_column_name)
    right_join_index, right_join_column = _get_join_column(right_table, right_column_name)

    # Create new columns to hold outputs from both tables 
    columns_from_left = []
    columns_from_right = []

    for c in left_table:
        n = table.Column(0, c.name, [], normal_type=c.type)
        n.nullable = c.nullable
        n.max_lenght = c.max_length

        columns_from_left.append(n)

    for c in right_table:
        n = table.Column(0, c.name, [], normal_type=c.type)
        n.nullable = c.nullable
        n.max_lenght = c.max_length

        columns_from_right.append(n)

    # Iterate over tables, keeping only rows with ids in both
    for left_index, v in enumerate(left_join_column):
        try:
            right_index = right_join_column.index(v)
        except ValueError:
            continue 

        for i, c in enumerate(left_table):
            columns_from_left[i].append(c[left_index])

        for i, c in enumerate(right_table):
            columns_from_right[i].append(c[right_index])

    # Drop duplicate id column
    del columns_from_right[right_join_index]

    # Build table from newly truncated columns
    jointab.extend(columns_from_left)
    jointab.extend(columns_from_right)

    print [i for i in jointab.rows()]

    return jointab

def full_outer_join(left_table, left_column_name, right_table, right_column_name):
    raise NotImplementedError()

def left_outer_join(left_table, left_column_name, right_table, right_column_name):
    raise NotImplementedError()

def right_outer_join(left_table, left_column_name, right_table, right_column_name):
    raise NotImplementedError()
