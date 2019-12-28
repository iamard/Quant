# coding=utf-8

from .Scraper import Scraper
from .TickerList import TickerList
from datetime import datetime
import logging as logging
import numpy as numpy
import json as json
import pandas as pandas
import time as time

class RTPrice(Scraper):
    def __init__(self):
        # Initialize Scraper class
        Scraper.__init__(self)

        # URL to create base connection
        self.__base = 'http://mis.twse.com.tw/stock/index.jsp'

    def quote_price_info(self, ticker_list, quote_date, logger):
        if isinstance(quote_date, str) == True:
            quote_date = datetime.strptime(quote_date, '%Y-%m-%d')
        
        ticker_dict = TickerList().quote_ticker_list(logger, refresh = False)
        ticker_dict = ticker_dict.to_dict('index')        
        ticker_info = []
        for ticker_id in ticker_list:
            ticker_type = ticker_dict.get(ticker_id)
            if ticker_type is None:
                return None
            ticker_type = ticker_type['ticker_type']
            if ticker_type == '上市':
                ticker_type = 'tse_{}.tw_'.format(ticker_id) + quote_date.strftime('%Y%m%d')
            else:
                ticker_type = 'otc_{}.tw_'.format(ticker_id) + quote_date.strftime('%Y%m%d')
            ticker_info.append(ticker_type)
            
        endpoint  = 'https://mis.twse.com.tw/stock/api/getStockInfo.jsp'
        tickers   = '|'.join(ticker_info)
        timestamp = int(time.time() * 1000 + 1000)
        cur_query = '{}?json=1&delay=0&ex_ch={}&_={}'.format(endpoint, \
            tickers, timestamp)

        data = self._handle_get_request_sync(self.__base)
        if data is None:
            return None

        data = self._handle_get_request_sync(cur_query)
        if data is None:
            return None
            
        data = json.loads(data)
        if data is None:
            return None

        columns = ['c', 'z', 'tv', 'v', 'o', 'h', 'l', 'y']
        frame = pandas.DataFrame(data['msgArray'], columns = columns)
        frame.columns = ['ticker_id', 'price', '當盤成交量', '累積成交量', \
            'open','最高價','最低價','昨收價']
        frame[['price', 'open']] = frame[['price', 'open']].astype(float)
        frame.dropna(inplace = True)
        frame = frame.set_index('ticker_id')
        
        print(frame)

        return frame

if __name__ == "__main__":
    realTime = RTPrice()
    data = realTime.quote_price_info(['2330', '1723', '1788'], '2019-07-05', logging.getLogger())
    print(data)
    data = realTime.quote_price_info(['2330', '1723', '1788'], '2019-07-15', logging.getLogger())
    print(data)