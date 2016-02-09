#!/usr/bin/env python


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


def sequential_join(left_rows, right_rows, header=True):
    """
    Join two tables by aligning them horizontally without performing any filtering.
    """
    len_left_headers = len(left_rows[0])
    len_right_headers = len(right_rows[0])

    if header:
        output = [left_rows[0] + right_rows[0]]
        left_rows = left_rows[1:]
        right_rows = iter(right_rows[1:])
    else:
        output = []

    for left_row in left_rows:
        try:
            right_row = next(right_rows)
            output.append(left_row + right_row)
        except StopIteration:
            output.append(left_row + [u''] * len_right_headers)

    for right_row in right_rows:
        output.append([u''] * len_left_headers + right_row)

    return output


def inner_join(left_rows, left_column_id, right_rows, right_column_id, header=True):
    """
    Execute an inner join on two tables and return the combined table.
    """
    len_left_headers = len(left_rows[0])

    if header:
        output = [left_rows[0] + right_rows[0]]
        left_rows = left_rows[1:]
        right_rows = right_rows[1:]
    else:
        output = []

    # Map right rows to keys
    right_mapped_keys = _get_mapped_keys(right_rows, right_column_id)

    for left_row in left_rows:
        len_left_row = len(left_row)

        if len_left_row < len_left_headers:
            left_row.extend([None] * (len_left_headers - len_left_row))

        left_key = left_row[left_column_id]

        if left_key in right_mapped_keys:
            for right_row in right_mapped_keys[left_key]:
                output.append(left_row + right_row)

    return output


def full_outer_join(left_rows, left_column_id, right_rows, right_column_id, header=True):
    """
    Execute full outer join on two tables and return the combined table.
    """
    len_left_headers = len(left_rows[0])
    len_right_headers = len(right_rows[0])

    if header:
        output = [left_rows[0] + right_rows[0]]
        left_rows = left_rows[1:]
        right_rows = right_rows[1:]
    else:
        output = []

    # Get ordered keys
    left_ordered_keys = _get_ordered_keys(left_rows, left_column_id)

    # Get mapped keys
    right_mapped_keys = _get_mapped_keys(right_rows, right_column_id)

    for left_row in left_rows:
        len_left_row = len(left_row)
        left_key = left_row[left_column_id]

        if len_left_row < len_left_headers:
            left_row.extend([None] * (len_left_headers - len_left_row))

        if left_key in right_mapped_keys:
            for right_row in right_mapped_keys[left_key]:
                output.append(left_row + right_row)
        else:
            output.append(left_row + ([u''] * len_right_headers))

    for right_row in right_rows:
        right_key = right_row[right_column_id]

        if right_key not in left_ordered_keys:
            output.append(([u''] * len_left_headers) + right_row)

    return output


def left_outer_join(left_rows, left_column_id, right_rows, right_column_id, header=True):
    """
    Execute left outer join on two tables and return the combined table.
    """
    len_left_headers = len(left_rows[0])
    len_right_headers = len(right_rows[0])

    if header:
        output = [left_rows[0] + right_rows[0]]
        left_rows = left_rows[1:]
        right_rows = right_rows[1:]
    else:
        output = []

    # Get mapped keys
    right_mapped_keys = _get_mapped_keys(right_rows, right_column_id)

    for left_row in left_rows:
        len_left_row = len(left_row)
        left_key = left_row[left_column_id]

        if len_left_row < len_left_headers:
            left_row.extend([None] * (len_left_headers - len_left_row))

        if left_key in right_mapped_keys:
            for right_row in right_mapped_keys[left_key]:
                output.append(left_row + right_row)
        else:
            output.append(left_row + ([u''] * len_right_headers))

    return output


def right_outer_join(left_rows, left_column_id, right_rows, right_column_id, header=True):
    """
    Execute right outer join on two tables and return the combined table.
    """
    len_left_headers = len(left_rows[0])

    if header:
        output = [left_rows[0] + right_rows[0]]
        left_rows = left_rows[1:]
        right_rows = right_rows[1:]
    else:
        output = []

    # Get ordered keys
    left_ordered_keys = _get_ordered_keys(left_rows, left_column_id)

    # Get mapped keys
    right_mapped_keys = _get_mapped_keys(right_rows, right_column_id)

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
            output.append(([u''] * len_left_headers) + right_row)

    return output
