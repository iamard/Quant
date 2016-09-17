# coding=utf-8

import numpy   as np
import pandas  as pd
import sqlite3 as sql

class Database():
    def __init__(self):
        self.__connx   = sql.connect("StockData.db", detect_types = sql.PARSE_DECLTYPES | sql.PARSE_COLNAMES)

    def __quote_schema(self, frame, name, index, flavor):
        command = "CREATE TABLE {name} (\n  ".format(name = name)

        if index == True:
            command += "{primary} TIMESTAMP PRIMARY KEY,\n  ".format(primary = frame.index.name)

        # Generate column types
        types   = frame.dtypes
        output  = []
        for index, key in enumerate(types.index):
            current = types[key]
            if issubclass(current.type, np.floating):
                current = "DOUBLE"
            output.append((key, current))
        columns = ',\n  '.join('%s %s' % x for x in output)
        command += columns
        command += ");"
        return command

    def writeFrame(self, frame, name, index = False, flavor = 'sqlite', if_exists = 'fail'):
        schema = self.__quote_schema(frame, name, index, "sqlite")
        return frame.to_sql(name, self.__connx, index = index, flavor = flavor, schema = schema, if_exists = if_exists)

    def readFrame(self, name, startDate = None, endDate = None):
        # Set the query command
        if startDate == None or endDate == None:
            query = "select * from {TABLE};".format(TABLE = name)
        else:
            query = "SELECT * from {TABLE} WHERE Date BETWEEN \'{START}\' AND \'{END}\';"
            query = query.format(TABLE = name, START = startDate, END = endDate)

        # Submit the query
        frame = pd.read_sql(query, self.__connx, index_col = "Date", parse_dates = ["Date"])
        frame = frame.sort_index(ascending = True)
        return frame
