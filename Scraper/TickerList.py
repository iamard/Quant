# coding=utf-8

from .Scraper import Scraper
from bs4 import BeautifulSoup
import os as os
import logging as logging
import pandas as pandas
import numpy as numpy
import asyncio as asyncio

class TickerList(Scraper):
    def __init__(self):
        # Initialize Scraper class
        Scraper.__init__(self)

        # URL to query stock codes
        self.__query = "https://isin.twse.com.tw/isin/C_public.jsp?strMode={TYPE}"

    def quote_ticker_list(self, logger, refresh = False, dump = 'csv', retry = 1):
        if dump == "csv":
            out_name = self.out_path + "tw_all_ticker_list.csv"
        elif dump == "xlsx":
            out_name = self.out_path + "tw_all_ticker_list.xlsx"
        else:
            return None

        if not refresh and os.path.exists(out_name):
            if dump == "csv":
                frame = pandas.read_csv(out_name, encoding = 'cp950')
            elif dump == "xlsx":
                frame = pandas.read_excel(out_name)
            frame['ticker_id'] = frame['ticker_id'].astype(str)
            frame = frame.set_index('ticker_id')
        else:
            ticker = {}
            for cur_type in range(2,5,2):
                query = self.__query.format(TYPE = cur_type)
                data  = self._handle_get_request_sync(query)
                if data is None:
                    logger.error('Quote ticker list failed')
                    return None

                soup   = BeautifulSoup(data, 'html.parser')
                table  = soup.find('table', {'class': 'h4'})
                rows   = table.findAll('tr')

                type  = ""
                for row in rows:
                    cols = row.findAll('td')
                    if len(cols) < 7:
                        type = cols[0].text.strip()
                    elif type == u"股票":
                        list = cols[0].text.split()
                        if cols[3].text == '上市' or \
                           cols[3].text == '上櫃':
                            if ticker.get(list[0]) == None:
                                ticker[list[0]] = [cols[2].text.replace('/', '-'), cols[3].text]
                            else:
                                print(list[0])
                        else:
                            logger.error('Quote ticker list failed')
                            return None
                                                                        
            frame = pandas.DataFrame.from_dict(ticker, orient = 'index')
            frame.columns = ['IPO_date', \
                             'ticker_type']
            frame.index.name = 'ticker_id'

            if dump == "csv":
                frame.to_csv(out_name, encoding = 'cp950')
            elif dump == "xlsx":
                frame.to_excel(out_name)
            
        return frame

if __name__ == "__main__":
    scraper = TickerList()
    scraper.quote_ticker_list(logging.getLogger(), refresh = True, dump = "csv")
    scraper.quote_ticker_list(logging.getLogger(), refresh = False, dump = "csv")