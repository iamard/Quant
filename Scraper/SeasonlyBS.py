# coding=utf-8

import os as os
import pandas as pandas
import numpy as numpy
import logging as logging
import asyncio as asyncio
import datetime as datetime
from bs4 import BeautifulSoup
from dateutil.rrule import *
from Scraper import Scraper

class SeasonlyBS(Scraper):
    def __init__(self):
        # Initialize Scraper class
        Scraper.__init__(self)

        # URL to query monthly revenue
        self.__query = 'https://mops.twse.com.tw/server-java/t164sb01?step=1&' \
            'CO_ID={TICKER_ID}&SYEAR={YEAR}&SSEASON={SEASON}&REPORT_ID=C'

    def trim_seasonly_bs(self, ticker_id, year, season, frame, dump = 'csv'):
        if dump == "csv":
            out_name = self.out_path + "{TICKER_ID}_{YEAR}_S{SEASON}_BS_trim.csv". \
                format(TICKER_ID = ticker_id, YEAR = year, SEASON = season)
        elif dump == "xlsx":
            out_name = self.put_path + "{TICKER_ID}_{YEAR}_S{SEASON}_BS_trim.xlsx". \
                format(TICKER_ID = ticker_id, YEAR = year, SEASON = season)
        else:
            return None

        frame = frame.reset_index()
        drop  = []
        for index, cur_row in frame.iterrows():
            cur_key = frame.loc[index, 'category']
            if cur_key.strip().endswith("權益總額"):
                frame.loc[index, 'category'] = cur_key.replace("權益總額", "權益總計")
            elif cur_key.strip().startswith("當期所得稅資產"):
                frame.loc[index, 'category'] = cur_key.replace("當期所得稅資產", "本期所得稅資產")
        
            if index > 1:            
                pre_key   = frame.loc[index - 1, 'category']
                cur_key   = frame.loc[index - 0, 'category']
                pre_level = len(pre_key) - len(pre_key.lstrip())
                cur_level = len(cur_key) - len(cur_key.lstrip())
                if cur_level > pre_level:
                    if cur_key.endswith("合計") or \
                       cur_key.endswith("總額") or \
                       cur_key.endswith("總計") or \
                       cur_key.endswith("淨額"):
                        frame.loc[index - 1, frame.columns[1:3]] = \
                        frame.loc[index - 0, frame.columns[1:3]]
                        drop.append(index - 0)
        frame = frame.drop(drop)
        frame = frame.set_index('category')

        if dump == "csv":
            frame.to_csv(out_name, encoding = 'cp950')
        elif dump == "xlsx":
            frame.to_excel(out_name)
        return frame

    async def quote_bs_core19(self, ticker_id, year, season, logger, refresh = False, dump = 'csv'):
        if dump == "csv":
            out_name = self.out_path + "{TICKER_ID}_{YEAR}_S{SEASON}_BS_orig.csv". \
                format(TICKER_ID = ticker_id, YEAR = year, SEASON = season)
        elif dump == "xlsx":
            out_name = self.put_path + "{TICKER_ID}_{YEAR}_S{SEASON}_BS_orig.xlsx". \
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
            logger.error(query)

            data  = await self._handle_get_request_async(query)
            if data is None:
                logger.error("Scraping {} {}-S{} BS failed!".format(ticker_id, year, season))
                return None
    
            soup  = BeautifulSoup(data, 'html.parser')
            div   = soup.find('div', { 'id': 'BalanceSheet' })
            table = div.find_next_sibling('table')
            if table is None:
                logger.error("Can't find {} {}-S{} BS tag".format(ticker_id, year, season))
                return None

            rows  = table.find_all('tr')
            found = False
            raw   = []
            for cur_row in range(0, len(rows)):
                heads = rows[cur_row].find_all('th')
                for cur_head in range(0, len(heads)):
                    title = heads[cur_head].find_all('span')
                    if title[0].text == '資產負債表':
                        found = True

                cols = rows[cur_row].find_all('td')
                if season != 4 and len(cols) > 4:
                    data = [cols[1].find_all('span')[0].text.replace('\t', ' '), \
                            cols[2].text.replace(',', ''), \
                            cols[4].text.replace(',', '')]
                    raw.append(data)
                elif season == 4 and len(cols) > 2:
                    data = [cols[1].find_all('span')[0].text.replace('\t', ' '), \
                            cols[2].text.replace(',', ''), \
                            cols[3].text.replace(',', '')]
                    raw.append(data)

            if found == False:
                logger.error("Can't find {} {}-S{} BS table".format(ticker_id, year, season))
                return None

            col_txt = ["{}-03-31", "{}-06-30", "{}-09-30", "{}-12-31"]
            frame   = pandas.DataFrame(raw)
            frame.columns = ['category', \
                             col_txt[season - 1].format(year - 0), \
                             col_txt[season - 1].format(year - 1)]
            frame = frame.set_index('category')
        
            if dump == "csv":
                frame.to_csv(out_name, encoding = 'cp950')
            elif dump == "xlsx":
                frame.to_excel(out_name)

        frame = self.trim_seasonly_bs(ticker_id, year, season, frame, dump)
        return (ticker_id, frame)

    async def quote_bs_core17(self, ticker_id, year, season, logger, refresh = False, dump = 'csv'):
        if season < 1 and season > 4:
            return None

        if dump == "csv":
            out_name = self.out_path + "{TICKER_ID}_{YEAR}_S{SEASON}_BS_orig.csv". \
                format(TICKER_ID = ticker_id, YEAR = year, SEASON = season)
        elif dump == "xlsx":
            out_name = self.put_path + "{TICKER_ID}_{YEAR}_S{SEASON}_BS_orig.xlsx". \
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
            logger.error(query)

            data  = await self._handle_get_request_async(query)
            if data == None:
                logger.error("Scraping {} {}-S{} BS failed!".format(ticker_id, year, season))
                return None

            soup  = BeautifulSoup(data, 'html.parser')
            raw   = []
            table = soup.find('table', attrs = {'class': 'result_table hasBorder'})
            if table == None:
                logger.error("Can't find {} {}-S{} BS tag".format(ticker_id, year, season))
                return None

            rows  = table.find_all('tr')
            found = False
            for cur_row in range(0, len(rows)):
                heads = rows[cur_row].find_all('th')
                for cur_head in range(0, len(heads)):
                    if heads[cur_head].text == '資產負債表':
                        found = True

                cols = rows[cur_row].find_all('td')
                if season != 4 and len(cols) > 3:
                    data = [cols[0].text[2:].replace('\t', ' '), \
                            cols[1].text.replace(',', ''), \
                            cols[3].text.replace(',', '')]
                    raw.append(data)
                elif season == 4 and len(cols) > 2:
                    data = [cols[0].text[2:].replace('\t', ' '), \
                            cols[1].text.replace(',', ''), \
                            cols[2].text.replace(',', '')]
                    raw.append(data)

            if found == False:
                logger.error("Can't find {} {}-S{} BS table".format(ticker_id, year, season))
                return None

            col_txt = ["{}-03-31", "{}-06-30", "{}-09-30", "{}-12-31"]
            frame   = pandas.DataFrame(raw)
            frame.columns = ['category', \
                             col_txt[season - 1].format(year - 0), \
                             col_txt[season - 1].format(year - 1)]
            frame = frame.set_index('category')
        
            if dump == "csv":
                frame.to_csv(out_name, encoding = 'cp950')
            elif dump == "xlsx":
                frame.to_excel(out_name)

        frame = self.trim_seasonly_bs(ticker_id, year, season, frame, dump)
        return (ticker_id, frame)

    def conv_date_to_season(self, date):
        seasons = {1: (datetime(date.year, 1, 1), datetime(date.year, 3, 31)),
                   2: (datetime(date.year, 4, 1), datetime(date.year, 6, 30)),
                   3: (datetime(date.year, 7, 1), datetime(date.year, 9, 30))}
        for season,(season_start, season_end) in seasons.items():
            if date >= season_start and date <= season_end:
                return season

        return 4

    def quote_seasonly_bs(self, ticker_list, start_date, end_date, \
        logger, refresh = False, dump = 'csv'):
        if(isinstance(start_date, str) == True or \
           isinstance(end_date, str) == True):
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date   = datetime.strptime(end_date, '%Y-%m-%d')

        season_set = set()
        for current in rrule(DAILY, dtstart = start_date, until = end_date):
            season_set.add((current.year, self.conv_date_to_season(current)))
            
        task_list = []
        for ticker_id in ticker_list:
            for season in season_set:
                if season[0] >= 2019:
                    task_list.append(asyncio.ensure_future( \
                        self.quote_bs_core19(ticker_id, \
                                             season[0], \
                                             season[1], \
                                             logger, \
                                             refresh)))
                else:
                    task_list.append(asyncio.ensure_future( \
                        self.quote_bs_core17(ticker_id, \
                                             season[0], \
                                             season[1], \
                                             logger, \
                                             refresh)))

        frame_dict = {}
        if len(task_list) > 0:
            event_loop   = asyncio.get_event_loop()
            task_done, _ = event_loop.run_until_complete(asyncio.wait(task_list))
            for curr_task in task_done:
                ticker_id, frame_data = curr_task.result()
                #print(frame_data.head(5))
                if frame_dict.get(ticker_id) is None:
                    frame_dict[ticker_id] = frame_data
                else:
                    frame_data = pandas.concat([frame_dict[ticker_id], frame_data], \
                                               axis = 1, \
                                               join = 'inner', \
                                               join_axes = [frame_data.index])
                    print(frame_data.head(5))
                    frame_dict[ticker_id] = frame_data[sorted(frame_data.columns)]
            return frame_dict
        else:
            return None

if __name__ == "__main__":
    scraper = SeasonlyBS()
    frame_dict = scraper.quote_seasonly_bs(['2454'], '2018-12-01', '2019-03-31', \
        logging.getLogger(), refresh = True, dump = "csv")
    frame_dict['2454'].to_csv('seasonly_bs_ut_case1.csv', encoding = 'cp950')
    #frame_dict = scraper.quote_seasonly_bs(['2454'], '2018-12-01', '2019-03-31', \
    #    logging.getLogger(), refresh = False, dump = "csv")
    #frame_dict['2454'].to_csv('seasonly_bs_ut_case2.csv', encoding = 'cp950')