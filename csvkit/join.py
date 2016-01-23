#!/usr/bin/env python

from copy import deepcopy


def _get_ordered_keys(rows, column_index):
    """
    Get ordered keys from rows, given the key column index.
    """
    return [r[column_index] for r in rows]

def _get_mapped_keys(rows, column_index, remove_column_index=False):
    mapped_keys = {}

    for r in rows:
        key = r[column_index]

        if remove_column_index:
            del r[column_index]

        if key in mapped_keys:
            mapped_keys[key].append(r)
        else:
            mapped_keys[key] = [r]

    return mapped_keys

def sequential_join(left_table, right_table):
    """
    Join two tables by aligning them horizontally without performing any filtering.
    """
    # Grab headers
    left_headers = left_table[0]
    right_headers = right_table[0]
    left_rows = left_table[1:]
    right_rows = iter(right_table[1:])

    output = [left_headers + right_headers]

    for left_row in left_rows:
        try:
            right_row = next(right_rows)
        except StopIteration:
            output.append(left_row + ([u''] * len(right_headers)))

        output.append(left_row + right_row)

    for right_row in right_rows:
        output.append(([u''] * len(left_headers)) + right_row)

    return output

def inner_join(left_table, left_column_id, right_table, right_column_id):
    """
    Execute an inner join on two tables and return the combined table.
    """
    # Grab headers
    left_headers = left_table[0]
    len_left_headers = len(left_headers)
    right_headers = right_table[0]
    left_rows = left_table[1:]
    right_rows = right_table[1:]

    # Map right rows to keys
    right_mapped_keys = _get_mapped_keys(right_rows, right_column_id)

    output = [left_headers + right_headers]

    for left_row in left_rows:
        len_left_row = len(left_row)

        if len_left_row < len_left_headers:
            left_row.extend([None] * (len_left_headers - len_left_row))

        left_key = left_row[left_column_id]

        if left_key in right_mapped_keys:
            for right_row in right_mapped_keys[left_key]:
                output.append(left_row + right_row)

    return output

def full_outer_join(left_table, left_column_id, right_table, right_column_id, no_duplicate_id_column=False):
    """
    Execute full outer join on two tables and return the combined table.
    """

    # Grab headers
    left_headers = left_table[0]
    len_left_headers = len(left_headers)
    right_headers = right_table[0]
    left_rows = left_table[1:]
    right_rows = right_table[1:]

    # Get ordered keys
    left_ordered_keys = _get_ordered_keys(left_rows, left_column_id)

    # Get mapped keys
    right_mapped_keys = _get_mapped_keys(deepcopy(right_rows), right_column_id, remove_column_index=no_duplicate_id_column)

    new_right_headers = right_headers
    if no_duplicate_id_column:
        del new_right_headers[right_column_id]

    output = [left_headers + new_right_headers]

    for left_row in left_rows:
        len_left_row = len(left_row)
        left_key = left_row[left_column_id]

        if len_left_row < len_left_headers:
            left_row.extend([None] * (len_left_headers - len_left_row))

        if left_key in right_mapped_keys:
            for right_row in right_mapped_keys[left_key]:
                output.append(left_row + right_row)
        else:
            output.append(left_row + ([u''] * len(right_headers)))

    for right_row in right_rows:
        right_key = right_row[right_column_id]

        if right_key not in left_ordered_keys:
            right_only_row = ([u''] * len(left_headers)) + right_row
            if no_duplicate_id_column:
                column_id = right_only_row.pop(len(left_headers) + right_column_id)
                right_only_row[left_column_id] = column_id
            output.append(right_only_row)

    return output

def left_outer_join(left_table, left_column_id, right_table, right_column_id):
    """
    Execute left outer join on two tables and return the combined table.
    """
    # Grab headers
    left_headers = left_table[0]
    len_left_headers = len(left_headers)
    right_headers = right_table[0]
    left_rows = left_table[1:]
    right_rows = right_table[1:]

    # Get mapped keys
    right_mapped_keys = _get_mapped_keys(right_rows, right_column_id)

    output = [left_headers + right_headers]

    for left_row in left_rows:
        len_left_row = len(left_row)
        left_key = left_row[left_column_id]

        if len_left_row < len_left_headers:
            left_row.extend([None] * (len_left_headers - len_left_row))

        if left_key in right_mapped_keys:
            for right_row in right_mapped_keys[left_key]:
                output.append(left_row + right_row)
        else:
            output.append(left_row + ([u''] * len(right_headers)))

    return output

def right_outer_join(left_table, left_column_id, right_table, right_column_id):
    """
    Execute right outer join on two tables and return the combined table.
    """
    # Grab headers
    left_headers = left_table[0]
    len_left_headers = len(left_headers)
    right_headers = right_table[0]
    left_rows = left_table[1:]
    right_rows = right_table[1:]

    # Get ordered keys
    left_ordered_keys = _get_ordered_keys(left_rows, left_column_id)

    # Get mapped keys
    right_mapped_keys = _get_mapped_keys(right_rows, right_column_id)

    output = [left_headers + right_headers]

    for left_row in left_rows:
        len_left_row = len(left_row)
        left_key = left_row[left_column_id]

        if len_left_row < len_left_headers:
            left_row.extend([None] * (len_left_headers - len_left_row))

        if left_key in right_mapped_keys:
            for right_row in right_mapped_keys[left_key]:
                output.append(left_row + right_row)

    for right_row in right_rows:
        right_key = right_row[right_column_id]

        if right_key not in left_ordered_keys:
            output.append(([u''] * len(left_headers)) + right_row)

    return output
