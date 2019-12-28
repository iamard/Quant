# coding=utf-8

from .Scraper import Scraper
from bs4 import BeautifulSoup
from io import StringIO
import os as os
import pandas as pandas
import numpy as numpy

class DailyRatio(Scraper):
    def __init__(self):
        # Initialize Scraper class
        Scraper.__init__(self)

    def quote_twse_data(self, year, month, day):
        query = 'http://www.twse.com.tw/exchangeReport/BWIBBU_d?' \
            'response=csv&date={YEAR}{MONTH}{DAY}&selectType=ALL'
        query = query.format(YEAR  = year, \
                             MONTH = str(month).zfill(2), \
                             DAY   = str(day).zfill(2))
        data = self._handle_get_request(query)
        if data == None:
            print("Get TWSE daily ratio failed\n")
            return None

        stream = StringIO(data)
        frame  = pandas.read_csv(stream, sep = ",", \
                                 skiprows = 1, usecols = [0, 1, 2, 3, 4], \
                                 skipfooter = 2, engine = 'python')
        frame.columns = ['ticker_id', \
                         'ticker_name', \
                         'P/E ratio', \
                         'yield(%)', \
                         'P/B ratio']
        frame = frame.set_index('ticker_id')
        return frame
    
    def quote_otc_data(self, year, month, day):
        query = 'https://www.tpex.org.tw/web/stock/aftertrading/peratio_analysis/pera_result.php?' \
            'l=zh-tw&o=csv&d={YEAR}/{MONTH}/{DAY}&c=&s=0,asc'
        query = query.format(YEAR  = year - 1911, \
                             MONTH = str(month).zfill(2), \
                             DAY   = str(day).zfill(2))
        data = self._handle_get_request(query)
        if data == None:
            print("Get OTC daily ratio failed\n")
            return None

        stream = StringIO(data)
        frame  = pandas.read_csv(stream, sep = ",", \
                                 skiprows = 3, usecols = [0, 1, 2, 5, 6], \
                                 skipfooter = 1, engine = 'python')    
        frame.columns = ['ticker_id', \
                         'ticker_name', \
                         'P/E ratio', \
                         'yield(%)', \
                         'P/B ratio']
        frame = frame.set_index('ticker_id')
        return frame      
        
    def quote_daily_ratio(self, year, month, day, refresh = False, dump = 'csv'):
        if dump == "csv":
            out_name = self.out_path + "taiwan_all_daily_ratio.csv"
        elif dump == "xlsx":
            out_name = self.out_path + "taiwan_all_daily_ratio.xlsx"
        else:
            return None
    
        if not refresh and os.path.exists(out_name):
            if dump == "csv":
                frame = pandas.read_csv(out_name, encoding = 'cp950')
            elif dump == "xlsx":
                frame = pandas.read_excel(out_name)
            frame = frame.set_index('ticker_id')
        else:
            twse_frame = self.quote_twse_data(year, month, day)
            otc_frame  = self.quote_otc_data(year, month, day)
            
            print(otc_frame)
            frame = pandas.concat([twse_frame, otc_frame])
            if dump == "csv":
                frame.to_csv(out_name, encoding = 'cp950')
            elif dump == "xlsx":
                frame.to_excel(out_name)

        return frame

if __name__ == "__main__":
    scraper = DailyRatio()
    scraper.quote_daily_ratio(2016, 7, 12, refresh = True, dump = 'csv')
    scraper.quote_daily_ratio(2016, 7, 12, refresh = False, dump = 'csv')