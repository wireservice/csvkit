#!/usr/bin/env python

import datetime

from sqlalchemy import Column, MetaData, Table, Integer
from sqlalchemy.schema import CreateTable

def make_column(column_name, normal_type, normal_column):
    for data in normal_column:
        if normal_type == bool:
            pass
        elif normal_type == int:
            pass
        elif normal_type == float:
            pass
        elif normal_type == datetime.datetime:
            pass
        elif normal_type == datetime.date:
            pass
        elif normal_type == datetime.time:
            pass
        elif normal_type == str:
            pass

    t = Integer

    column = Column(column_name, t)

    return column

def make_create_table(column_names, normal_types, normal_columns):
    metadata = MetaData()
    table = Table('csvsql', metadata)

    for i in range(len(column_names)):
        c = make_column(column_names[i], normal_types[i], normal_columns[i])
        table.append_column(c)
    
    return CreateTable(table).compile()
