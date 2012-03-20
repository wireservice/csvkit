#!/usr/bin/env python
from itertools import groupby


def group_rows(header, rows, grouped_column_ids, count_column_name=None, grouped_only=False):
    """
    Given a list of rows (header row first), group by given column ids
    grouped_column_ids should be zero indexed
    """
    #Define key fn that makes tuple of given indices from row
    keyfn = lambda x: tuple(x[i] for i in grouped_column_ids)

    #Sort the rows first
    rows.sort(key=keyfn)

    #First row of output is header
    if grouped_only:
        header = list(keyfn(header))
    if count_column_name:
        header.append(count_column_name)
    output = [header] if header is not None else []

    #Group
    for group, group_rows in groupby(rows, key=keyfn):
        group_rows = list(group_rows)
        count = len(group_rows)
        #Output first row only of each group
        out_row = group_rows[0]
        if grouped_only:
            out_row = list(keyfn(out_row))
        if count_column_name:
            out_row.append(count)
        output.append(out_row)

    return output
