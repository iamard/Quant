# coding=utf-8

from Crawler import Crawler
from StringIO import StringIO
import pandas as pandas
from dateutil import parser

class DailyTrade(Crawler):
    def __init__(self):
        # Initialize Crawler class
        Crawler.__init__(self)

        # Real URL to acquire information
        self.__query = 'http://www.twse.com.tw/ch/trading/exchange/STOCK_DAY/STOCK_DAYMAIN.php'
        self.__data  = {'download': 'csv', 'query_year': '', 'query_month': '', 'CO_ID':''}

    def __add_1911_to_year(self, date):
        try:
            date = parser.parse(date)
            date = ('-').join([str(date.year + 1911), str(date.month), str(date.day)])
        except ValueError:
            return pandas.NaT
        return date

    def __string_to_float(self, string):
        try:
            return float(''.join(x for x in string if x.isdigit()))
        except:
            return float('nan')
        
    def quote_daily_trade(self, code, year, month, dump = None):
        self.__data['query_year'] = year
        self.__data['query_month'] = month
        self.__data['CO_ID'] = code
        
        data  = self._handle_post_request(self.__query, self.__data, 'cp950')
        if data == None:
            print("Can't query daily trade info")
            return None

        # Create data frame
        frame = pandas.read_csv(StringIO(data), 
                                encoding = 'utf8', 
                                sep = ',', 
                                skiprows = 1,
                                header = 0,
                                index_col = 0,
                                usecols = [0, 1, 2, 3, 4, 5, 6, 7, 8],
                                parse_dates = True, 
                                date_parser = self.__add_1911_to_year)
        frame = frame.dropna(how = 'all')

        if len(frame.index) == 0:
            print("Can't query daily trade info for " + code)
            return None

        frame[u"成交股數"] = frame[u"成交股數"].apply(self.__string_to_float)
        frame[u"成交金額"] = frame[u"成交金額"].apply(self.__string_to_float)
        frame[u"成交筆數"] = frame[u"成交筆數"].apply(self.__string_to_float)

        if dump == "csv":
            frame.to_csv("{CODE}_{YEAR}_{MONTH}-DailyTrade.csv".format(CODE = code, YEAR = year, MONTH = month), encoding = 'cp950')
        elif dump == "xlsx":
            frame.to_excel("{CODE}_{YEAR}_{MONTH}-DailyTrade.xlsx".format(CODE = code, YEAR = year, MONTH = month))

        return frame

if __name__ == "__main__":
    crawler = DailyTrade()
    frame   = crawler.quote_daily_trade('1101', 2013, 8, dump = 'csv')
    #frame   = crawler.quote_daily_trade('1256', 2013, 8, dump = 'csv')
    print frame.head(10)
