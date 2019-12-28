# coding=utf-8

from .Scraper import Scraper
from bs4 import BeautifulSoup
from dateutil.rrule import *
from dateutil.relativedelta import *
import os as os
import math as math
import logging as logging
import asyncio as asyncio
import pandas as pandas

class MonthlyRev(Scraper):
    def __init__(self):
        # Initialize Scraper class
        Scraper.__init__(self)

        # URL to query monthly revenue
        self.__query = 'https://mops.twse.com.tw/nas/t21/{TYPE}/t21sc03_{YEAR}_{MONTH}_0.html'

    def convert_str_to_float(self, value):
        try:
            return float(value)
        except ValueError:
            return float('nan')
        
    async def quote_revenue_core(self, year, month, logger, refresh = False, dump = 'csv'):
        if dump == "csv":
            out_name = self.out_path + "tw_{YEAR}-{MONTH}_rev.csv". \
                format(YEAR = year, MONTH = month)
        elif dump == "xlsx":
            out_name = self.out_path + "tw_{YEAR}-{MONTH}_rev.xlsx". \
                format(YEAR = year, MONTH = month)
        else:
            return None

        if not refresh and os.path.exists(out_name):
            if dump == "csv":
                frame = pandas.read_csv(out_name, encoding = 'cp950')
            elif dump == "xlsx":
                frame = pandas.read_excel(out_name)
            curr_month = '{}-{}'.format(year - 0, str(month).zfill(2))
            frame[[curr_month]] = frame[[curr_month]].astype(float)
            frame['ticker_id']  = frame['ticker_id'].astype(str)
            frame = frame.set_index('ticker_id')
        else:
            typeList = ['sii', 'otc']
            rawData  = []
            output   = None
            hasNan   = False
            for type in typeList:
                query = self.__query.format(TYPE = type, YEAR = year - 1911, MONTH = month)
                data  = await self._handle_get_request_async(query)
                if data == None:
                    logger.error("Scrape {}-{} revenue failed\n".format(year, month))
                    return None

                soup   = BeautifulSoup(data, 'html.parser')
                while(True):
                    table = soup.find('table', attrs = {'border': '5'})
                    if table == None:
                        break
                    rows  = table.find_all('tr')
                    for index in range(0, len(rows) - 1):
                        cols  = rows[index].find_all('td')
                        if len(cols) > 0:
                            value  = self.convert_str_to_float(cols[2].text.replace(',', ''))
                            if hasNan == False:
                                hasNan = math.isnan(value)
                            data   = [cols[0].text, \
                                      #cols[1].text, \
                                      value, \
                                      #cols[3].text.replace(',', ''), \
                                      #cols[4].text.replace(',', ''), \
                                      #cols[5].text.replace(',', ''), \
                                      #cols[5].text.replace(',', ''), \
                                      #cols[7].text.replace(',', ''), \
                                      #cols[8].text.replace(',', ''), \
                                      #cols[9].text.replace(',', ''), \
                                      #cols[10].text.replace(',', '')
                                     ]
                            rawData.append(data)
                    table.decompose()
        
            if len(rawData) == 0:
                logger.error("Scrape {}-{} revenue failed\n".format(year, month))
                return None
        
            frame = pandas.DataFrame(rawData)
        
            curr_month = '{}-{}'.format(year - 0, str(month).zfill(2))
            #if month > 1:
            #    prev_month = '{}-{}'.format(year - 0, str(month - 1).zfill(2))
            #else:
            #    prev_month = '{}-{}'.format(year - 1, 12)
            #prev_year  = '{}-{}'.format(year - 1, str(month).zfill(2))
            frame.columns = ['ticker_id', \
                             #'公司名稱', \
                             curr_month, \
                             #prev_month, \
                             #prev_year, \
                             #'上月比較增減(%)', \
                             #'去年同月增減(%)', \
                             #'當月累計營收', \
                             #'去年累計營收', \
                             #'前期比較增減(%)', \
                             #'備註'
                             ]
            #frame[[curr_month]] = frame[[curr_month]].astype(float)
            frame['ticker_id']  = frame['ticker_id'].astype(str)
            frame = frame.set_index('ticker_id')
        
            if hasNan == False:
                if dump == "csv":
                    frame.to_csv(out_name, encoding = 'cp950')
                elif dump == "xlsx":
                    frame.to_excel(out_name)

        return frame.sort_index()

    def quote_monthly_revenue(self, start_date, end_date, \
        logger, refresh = False, dump = 'csv', retry = 1):
        if(isinstance(start_date, str) == True or \
           isinstance(end_date, str) == True):
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date   = datetime.strptime(end_date, '%Y-%m-%d')
        
        start_date = start_date - relativedelta(months = 1)
        task_list  = []
        frame_data = None
        for current in rrule(MONTHLY, dtstart = start_date, until = end_date):
            task_list.append(asyncio.ensure_future( \
                self.quote_revenue_core(current.year, \
                                        current.month, \
                                        logger, \
                                        refresh = False)))

        frame_list  = []
        if len(task_list) > 0:
            event_loop   = asyncio.get_event_loop()        
            task_done, _ = event_loop.run_until_complete(asyncio.wait(task_list))
            for curr_task in task_done:
                frame_data = curr_task.result()
                if frame_data is not None:
                    frame_list.append(frame_data)

        if len(frame_list) > 0:
            frame_data = pandas.concat(frame_list, sort = True, axis = 1)
            frame_data.index.name = 'month'
            frame_data = frame_data.T
            frame_data = frame_data.reset_index()
            columns = list(frame_data.columns)
            columns[0] = 'month'
            frame_data.columns = columns
            frame_data = frame_data.set_index('month')
            frame_data = frame_data.sort_index(axis = 0, ascending = True)

            logger.info(frame_data.head(5))
            return frame_data
        else:
            return None
        
if __name__ == "__main__":
    scraper = MonthlyRev()
    scraper.quote_monthly_revenue('2018-05-01', '2019-05-01', logging.getlogger(), \
        refresh = True, dump = "csv")
    scraper.quote_monthly_revenue('2018-05-01', '2019-05-01', logging.getlogger(), \
        refresh = False, dump = "csv")
