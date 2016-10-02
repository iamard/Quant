# coding=utf-8

import numpy   as numpy
import pandas  as pandas
import sqlite3 as sql3
import threading as thread

class Database():
    __lock = thread.Lock()  

    def __init__(self):
        self.__connx = sql3.connect("StockData.db", detect_types = sql3.PARSE_DECLTYPES | sql3.PARSE_COLNAMES)
        
    def _quote_data_schema(self, frame, name, index, flavor):
        command = "CREATE TABLE {name} (\n  ".format(name = name)

        if index == True:
            command += "{primary} TIMESTAMP PRIMARY KEY,\n  ".format(primary = frame.index.name)

        # Generate column types
        types   = frame.dtypes
        output  = []
        for index, key in enumerate(types.index):
            current = types[key]
            if issubclass(current.type, numpy.floating):
                current = "DOUBLE"
            output.append((key, current))
        columns = ',\n  '.join('%s %s' % x for x in output)
        command += columns
        command += ");"
        return command

    def write_data_frame(self, frame, name, index = False, flavor = 'sqlite', if_exists = 'fail'):
        schema = self._quote_data_schema(frame, name, index, "sqlite")
        with self.__lock:
            return frame.to_sql(name, self.__connx, index = index, flavor = flavor, schema = schema, if_exists = if_exists)

    def read_data_frame(self, name, startDate = None, endDate = None):
        # Set the query command
        if startDate == None or endDate == None:
            query = "select * from {TABLE};".format(TABLE = name)
        else:
            query = "SELECT * from {TABLE} WHERE Date BETWEEN \'{START}\' AND \'{END}\';"
            query = query.format(TABLE = name, START = startDate, END = endDate)

        # Submit the query
        with self.__lock:
            frame = pandas.read_sql(query, self.__connx, index_col = "Date", parse_dates = ["Date"])
        frame = frame.sort_index(ascending = True)
        return frame
