#!/usr/bin/env python

from csvkit import table

class JoinError(Exception):
    """
    Exception raised when there is a problem joing tables.
    """
    def __init__(self, msg):
        self.msg = msg

def _get_join_column(headers, column_name):
    """
    Get the column that should be used for making the join. 
    """
    try:
        index = headers.index(column_name)
    except ValueError:
        raise JoinError('Table does not have a column named "%s"' % column_name)

    return index

def _get_ordered_keys(rows, column_index):
    """
    Get ordered keys from rows, given the key column index.
    """
    return [r[column_index] for r in rows]

def _get_mapped_keys(rows, column_index):
    mapped_keys = {}

    for r in rows:
        key = r[column_index]

        if key in mapped_keys:
            mapped_keys[key].append(r)
        else:
            mapped_keys[key] = [r]

    return mapped_keys

def inner_join(left_table, left_column_name, right_table, right_column_name):
    """
    Execute an inner join on two tables and return the combined table.
    """
    output = []

    # Grab headers
    left_headers = left_table[0]
    right_headers = right_table[0]
    left_rows = left_table[1:]
    right_rows = right_table[1:]

    # Get the columns which will function as keys 
    left_column_index = _get_join_column(left_headers, left_column_name)
    right_column_index = _get_join_column(right_headers, right_column_name)

    # Get ordered keys
    #left_ordered_keys = _get_ordered_keys(left_rows, left_column_index)
    #right_ordered_keys = _get_ordered_keys(right_rows, right_column_index)

    # Get mapped keys
    #left_mapped_keys = _get_mapped_keys(left_rows, left_column_index)
    right_mapped_keys = _get_mapped_keys(right_rows, right_column_index)

    output.append(left_headers + right_headers)

    for left_row in left_rows:
        left_key = left_row[left_column_index]

        if left_key in right_mapped_keys:
            for right_row in right_mapped_keys[left_key]:
                output.append(left_row + right_row)

    return output

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
    """
    Execute left outer join on two tables and return the combined table.
    """
    jointab = table.Table()
    
    # Get the columns which will function as keys 
    left_join_index, left_join_column, left_as_set = _get_join_column(left_table, left_column_name)
    right_join_index, right_join_column, right_as_set = _get_join_column(right_table, right_column_name)
    
    # Left outer join = left keys only
    joined_keys = sorted(left_join_column)
    
    # Create a column to hold key values
    key_column = table.Column(0, left_join_column.name, [], normal_type=left_join_column.type)

    # Create new columns to hold outputs from both tables 
    columns_from_left = _clone_columns_empty(left_table)
    columns_from_right = _clone_columns_empty(right_table)

    # Iterate over joined keys, adding column values from both tables
    for v in joined_keys:
        key_column.append(v)

        i = left_join_column.index(v)

        for j, c in enumerate(left_table):
            columns_from_left[j].append(c[i])

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

def right_outer_join(left_table, left_column_name, right_table, right_column_name):
    """
    Execute right outer join on two tables and return the combined table.
    """
    jointab = table.Table()
    
    # Get the columns which will function as keys 
    left_join_index, left_join_column, left_as_set = _get_join_column(left_table, left_column_name)
    right_join_index, right_join_column, right_as_set = _get_join_column(right_table, right_column_name)
    
    # Left outer join = left keys only
    joined_keys = sorted(right_join_column)
    
    # Create a column to hold key values
    key_column = table.Column(0, left_join_column.name, [], normal_type=left_join_column.type)

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

        i = right_join_column.index(v)

        for j, c in enumerate(right_table):
            columns_from_right[j].append(c[i])

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
