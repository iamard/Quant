# coding=utf-8

import os as os
import pandas as pandas
import numpy as numpy
import logging as logging
from bs4 import BeautifulSoup
from .Scraper import Scraper

class SeasonlyIS(Scraper):
    def __init__(self):
        # Initialize Scraper class
        Scraper.__init__(self)

        # URL to query monthly revenue
        self.__query = 'https://mops.twse.com.tw/server-java/t164sb01?step=1&' \
            'CO_ID={TICKER_ID}&SYEAR={YEAR}&SSEASON={SEASON}&REPORT_ID=C'

    def trim_seasonly_is(self, ticker_id, year, season, frame, dump = 'csv'):
        if dump == "csv":
            out_name = self.out_path + "{TICKER_ID}_{YEAR}_S{SEASON}_IS_trim.csv". \
                format(TICKER_ID = ticker_id, YEAR = year, SEASON = season)
        elif dump == "xlsx":
            out_name = self.put_path + "{TICKER_ID}_{YEAR}_S{SEASON}_IS_trim.xlsx". \
                format(TICKER_ID = ticker_id, YEAR = year, SEASON = season)
        else:
            return None

        frame = frame.reset_index()
        for index, cur_row in frame.iterrows():
            if index > 1:            
                pre_key   = frame.loc[index - 1, 'category']
                cur_key   = frame.loc[index - 0, 'category']
                pre_level = len(pre_key) - len(pre_key.lstrip())
                cur_level = len(cur_key) - len(cur_key.lstrip())
                if cur_key.endswith("本期淨利（淨損）"):
                    frame.loc[index, 'category'] = \
                        cur_key.replace("本期淨利（淨損）", \
                                        "本期稅後淨利（淨損）")
                elif cur_level > pre_level and \
                     cur_key.endswith("繼續營業單位淨利（淨損）"):
                    if pre_key.endswith("基本每股盈餘"):
                        frame.loc[index, 'category'] = \
                            cur_key.replace("繼續營業單位淨利（淨損）", \
                                            "繼續營業單位淨利（淨損）－基本")
                    elif pre_key.endswith("稀釋每股盈餘"):
                        cur_key.replace("繼續營業單位淨利（淨損）", \
                                        "繼續營業單位淨利（淨損）－稀釋")
        frame = frame.set_index('category')

        if dump == "csv":
            frame.to_csv(out_name, encoding = 'cp950')
        elif dump == "xlsx":
            frame.to_excel(out_name)
        return frame
            
    def quote_seasonly_is(self, ticker_id, year, season, logger, refresh = False, dump = 'csv'):
        if season < 1 and season > 4:
            return None

        if dump == "csv":
            out_name = self.out_path + "{TICKER_ID}_{YEAR}_S{SEASON}_IS_orig.csv". \
                format(TICKER_ID = ticker_id, YEAR = year, SEASON = season)
        elif dump == "xlsx":
            out_name = self.put_path + "{TICKER_ID}_{YEAR}_S{SEASON}_IS_orig.xlsx". \
                format(TICKER_ID = ticker_id, YEAR = year, SEASON = season)
        else:
            return None
            
        if not refresh and os.path.exists(out_name):
            if dump == "csv":
                frame = pandas.read_csv(out_name, encoding = 'cp950')
            elif dump == "xlsx":
                frame = pandas.read_excel(out_name)
            frame = frame.set_index('category')
        else: 
            query = self.__query.format(TICKER_ID = ticker_id, YEAR = year, SEASON = season)
            data  = self._handle_get_request(query)
            if data == None:
                logger.error("Scraping {} {}-S{} IS failed!".format(ticker_id, year, season))
                return None

            soup  = BeautifulSoup(data, 'html.parser')
            raw   = []
            table = soup.find('table', attrs = {'class': 'main_table hasBorder'})
            if table == None:
                logger.error("Can't find {} {}-S{} IS tag".format(ticker_id, year, season))
                return None

            rows  = table.find_all('tr')
            found = False
            for cur_row in range(0, len(rows)):
                heads = rows[cur_row].find_all('th')
                for cur_head in range(0, len(heads)):
                    if heads[cur_head].text == '綜合損益表':
                        found = True
            
                cols = rows[cur_row].find_all('td')
                if len(cols) > 2:
                    data = [cols[0].text, \
                            cols[1].text.replace(',', ''), \
                            cols[2].text.replace(',', '')]
                    raw.append(data)

            if found == False or len(raw) == 0:
                logger.error("Can't find {} {}-S{} IS table".format(ticker_id, year, season))
                return None
                    
            col_txt = ["{}-03-31", "{}-06-30", "{}-09-30", "{}-12-31"]
            frame   = pandas.DataFrame(raw)
            frame.columns = ['category', \
                             col_txt[season - 1].format(year - 0),
                             col_txt[season - 1].format(year - 1)]
            frame = frame.set_index('category')
        
            if dump == "csv":
                frame.to_csv(out_name, encoding = 'cp950')
            elif dump == "xlsx":
                frame.to_excel(out_name)

        frame = self.trim_seasonly_is(ticker_id, year, season, frame, dump)
        return frame

if __name__ == "__main__":
    scraper = SeasonlyIS()
    scraper.quote_seasonly_is(1337, 2019, 1, logging.getLogger(), refresh = True, dump = "csv")
    scraper.quote_seasonly_is(1337, 2019, 1, logging.getLogger(), refresh = False, dump = "csv")