#!/usr/bin/env python

import datetime

from sqlalchemy import Column, MetaData, Table
from sqlalchemy import Boolean, Date, DateTime, Float, Integer, String, Time
from sqlalchemy.schema import CreateTable

DIALECTS = {
    'access': 'access.base',
    'firebird': 'firebird.kinterbasdb',
    'informix': 'informix.informixdb',
    'maxdb': 'maxdb.sapdb',
    'mssql': 'mssql.pyodbc',
    'mysql': 'mysql.mysqlconnector',
    'oracle': 'oracle.cx_oracle',
    'postgresql': 'postgresql.psycopg2',
    'sqlite': 'sqlite.pysqlite',
    'sybase': 'sybase.pyodbc'
}

def make_column(column):
    """
    Creates a sqlalchemy column from a csvkit Column.
    """
    sql_column_kwargs = {'nullable': False}
    sql_type_kwargs = {}

    if column.type == bool:
        sql_column_type = Boolean  
    elif column.type == int:
        sql_column_type = Integer
    elif column.type == float:
        sql_column_type = Float
    elif column.type == datetime.datetime:
        sql_column_type = DateTime
    elif column.type == datetime.date:
        sql_column_type = Date
    elif column.type == datetime.time:
        sql_column_type = Time
    elif column.type == None:
        sql_column_type = String
        sql_type_kwargs['length'] = 32
    elif column.type == unicode:
        sql_column_type = String
        sql_type_kwargs['length'] = max([len(d) if d else 0 for d in column])
    else:
        raise ValueError('Unexpected normalized column type: %s' % column.type)

    for d in column:
        if d == None:
            sql_column_kwargs['nullable'] = True
            break

    column = Column(column.name, sql_column_type(**sql_type_kwargs), **sql_column_kwargs)

    return column

def make_table(table, name='table_name'):
    """
    Creates a sqlalchemy table from a csvkit Table.
    """
    metadata = MetaData()
    sql_table = Table(name, metadata)

    for column in table:
        sql_table.append_column(make_column(column))

    return sql_table

def make_create_table_statement(sql_table, dialect=None):
    """
    Generates a CREATE TABLE statement for a sqlalchemy table.
    """
    if dialect:
        module = __import__('sqlalchemy.dialects.%s' % DIALECTS[dialect], fromlist=['dialect'])
        dialect = module.dialect() 

    return unicode(CreateTable(sql_table).compile(dialect=dialect)).strip()
