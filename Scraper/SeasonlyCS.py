# coding=utf-8

import os as os
import pandas as pandas
import numpy as numpy
from bs4 import BeautifulSoup
from .Scraper import Scraper

class SeasonlyCS(Scraper):
    def __init__(self):
        # Initialize Scraper class
        Scraper.__init__(self)

        # URL to query monthly revenue
        self.__query = 'https://mops.twse.com.tw/server-java/t164sb01?step=1&' \
            'CO_ID={TICKER_ID}&SYEAR={YEAR}&SSEASON={SEASON}&REPORT_ID=C'

    def quote_seasonly_cs(self, ticker_id, year, season, refresh = False, dump = "csv"):
        if season < 1 and season > 4:
            return None

        if dump == "csv":
            out_name = self.out_path + "{TICKER_ID}_{YEAR}_S{SEASON}_CS_orig.csv". \
                format(TICKER_ID = ticker_id, YEAR = year, SEASON = season)
        elif dump == "xlsx":
            out_name = self.put_path + "{TICKER_ID}_{YEAR}_S{SEASON}_CS_orig.xlsx". \
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
                print("Scrape {} {}-{} CS failed\n", ticker_id, year, season)
                return None

            soup  = BeautifulSoup(data, 'html.parser')
            raw   = []
            table = soup.find_all('table', attrs = {'class': 'main_table hasBorder'})
            if table == None or len(table) <= 1:
                print("Can't find CS table tag!\n")
                return None

            table = table[1]
            rows  = table.find_all('tr')
            found = False

            rows  = table.find_all('tr')
            for cur_row in range(0, len(rows)):
                heads = rows[cur_row].find_all('th')
                for cur_head in range(0, len(heads)):
                    if heads[cur_head].text == '現金流量表':
                        found = True

                cols = rows[cur_row].find_all('td')
                if len(cols) > 2:
                    data = [cols[0].text, \
                            cols[1].text.replace(',', ''), \
                            cols[2].text.replace(',', '')]
                    raw.append(data)

            if found == False or len(raw) == 0:
                print("Can't find cash statement")
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

        return frame

if __name__ == "__main__":
    scraper = SeasonlyCS()
    scraper.quote_seasonly_cs(2454, 2018, 1, refresh = True, dump = "csv")
    scraper.quote_seasonly_cs(2454, 2018, 1, refresh = False, dump = "csv")