# coding=utf-8

import datetime as datetime
import os as os
import logging as logging
import pandas as pandas
import time as time
import json as json
import numpy as numpy
import asyncio as asyncio
from .Scraper import Scraper
from .TickerList import TickerList

class DailyPrice(Scraper):
    def __init__(self):
        # Initialize Scraper class
        Scraper.__init__(self)

        self.__query = 'https://query1.finance.yahoo.com'
        
    async def quote_price_core(self, ticker_id, start_date, end_date, \
            logger, refresh = False, retry = 1):    
        logger.info('Try scraping ' + ticker_id + ' price')
        query = "{}/v8/finance/chart/{}".format(self.__query, ticker_id)
        start = None
        end   = None
        if start_date is None:
            start = -2208988800
        elif isinstance(start_date, datetime.datetime):
            start = int(time.mktime(start_date.timetuple()))
        elif isinstance(start_date, str):
            start = int(time.mktime(time.strptime(start_date, '%Y-%m-%d')))
        else:
            logger.error('Unknown start date type error')
            return (ticker_id, None)
        
        if end_date is None:
            end = int(time.time())
        elif isinstance(end_date, datetime.datetime):
            end = int(time.mktime(end_date.timetuple()))
        elif isinstance(end_date, str):
            end = int(time.mktime(time.strptime(end_date, '%Y-%m-%d')))
        else:
            logger.error('Unknown end date type error')
            return (ticker_id, None)

        params = {"period1": start, "period2": end}
        params["interval"] = '1d'
        params["includePrePost"] = 'true'
        params["events"] = "div,splits"

        logger.error('Scraping ' + ticker_id + ' price start!')
        data = await self._handle_get_request_async(query, params)
        logger.error('Scraping ' + ticker_id + ' price done!')
            
        if data is None or "Will be right back" in data:
            logger.error('Scraping ' + ticker_id + ' price failed!')
            return (ticker_id, None)

        data = json.loads(data)
        if "chart" in data and data["chart"]["error"]:
            logger.error('Scraping ' + ticker_id + ' price failed!')
            return None
        elif "chart" not in data or data["chart"]["result"] is None or \
             len(data["chart"]["result"]) == 0:
            logger.error('Scraping ' + ticker_id + ' price failed!')
            return (ticker_id, None)
        try:
            array = data["chart"]["result"][0]
            timestamps = array["timestamp"]
            ohlc = array["indicators"]["quote"][0]
            volumes = ohlc["volume"]
            opens = ohlc["open"]
            closes = ohlc["close"]
            lows = ohlc["low"]
            highs = ohlc["high"]

            adjclose = closes
            if "adjclose" in array["indicators"]:
                adjclose = array["indicators"]["adjclose"][0]["adjclose"]

            frame = pandas.DataFrame({"open": opens,
                                      "high": highs,
                                      "low": lows,
                                      "close": closes,
                                      "adj_close": adjclose,
                                      "volume": volumes})

            frame.index = pandas.to_datetime(timestamps, unit = 's')
            frame.sort_index(inplace = True, ascending = True)
            
            frame = numpy.round(frame, data["chart"]["result"][0]["meta"]["priceHint"])
            frame['volume'] = frame['volume'].fillna(0).astype(numpy.int64)
            frame.dropna(inplace = True)

            frame.index = frame.index.tz_localize("UTC").tz_convert( \
                data["chart"]["result"][0]["meta"]["exchangeTimezoneName"])
            
            frame.index = pandas.to_datetime(frame.index.date, format = '%Y-%m-%d')
            frame.index.name = "date"
        except:
            logger.error('Scraping ' + ticker_id + ' price failed!')
            return (ticker_id, None)
                
        frame[['open', 'high', 'low', 'close', 'adj_close', 'volume']]= \
        frame[['open', 'high', 'low', 'close', 'adj_close', 'volume']].astype(float)

        #frame = frame.reset_index()
        #frame = frame.sort_values(by = ['date'], ascending = True)
        #frame_data[['date']] = frame_data[['date']].astype(object)
        #frame = frame.set_index('date')

        return (ticker_id, frame)
    
    async def quote_price_start(self, tasks):
        result = await asyncio.gather(*tasks)
        return result
    
    def quote_daily_price(self, ticker_list, start_date, end_date, \
            logger, refresh = False, dump = 'csv', retry = 1):

        if isinstance(start_date, str) == True:
            start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        
        if isinstance(end_date, str) == True:
            end_date   = datetime.datetime.strptime(end_date, '%Y-%m-%d')

        ticker_dict = TickerList().quote_ticker_list(logger, refresh = False)
        ticker_dict = ticker_dict.to_dict('index')

        print("ticker list {}".format(ticker_list))

        task_list   = []
        frame_dict  = {}
        for ticker_id in ticker_list:
            print("quote => {}".format(ticker_id))
        
            output_name = None
            if dump == "csv":
                output_name = self.out_path + "{}_daily_price.csv".format(ticker_id)
            elif dump == "xlsx":
                output_name = self.out_path + "{}_daily_price.xlsx".format(ticker_id)

            frame_data = None
            if not refresh and os.path.exists(output_name):
                if output_name.endswith('csv'):
                    frame_data = pandas.read_csv(output_name, encoding = 'cp950')
                elif output_name.endswith('xlsx'):
                    frame_data = pandas.read_excel(output_name)
                frame_data = frame_data.sort_values(by = ['date'], ascending = True)

                min_date = datetime.datetime.strptime(frame_data.iloc[0]['date'].split(' ')[0], '%Y-%m-%d')
                max_date = datetime.datetime.strptime(frame_data.iloc[-1]['date'].split(' ')[0], '%Y-%m-%d')
                if min_date <= start_date and end_date <= max_date:
                    mask = (frame_data['date'] >= datetime.datetime.strftime(start_date, '%Y-%m-%d')) & \
                           (frame_data['date'] <= datetime.datetime.strftime(end_date, '%Y-%m-%d'))
                    frame_data = frame_data[mask]
                    frame_data[['open', 'high', 'low', 'close', 'adj_close', 'volume']]= \
                        frame_data[['open', 'high', 'low', 'close', 'adj_close', 'volume']].astype(float)
                    
                    #frame_data[['date']] = frame_data[['date']].astype(object)
                    frame_data = frame_data.set_index('date')
                    frame_data.index = pandas.to_datetime(frame_data.index, format = '%Y-%m-%d')
                else:
                    #logger.error('Set frame data to None')
                    frame_data = None
                    
            if frame_data is not None:
                frame_dict[ticker_id] = frame_data
                continue
            else:
                ticker_type  = ticker_dict.get(ticker_id, None)
                ticker_quote = None
                if ticker_type is None:
                    if ticker_id.endswith('tw') or \
                       ticker_id.endswith('two'):
                        ticker_quote = ticker_id
                    else:
                        ticker_quote = ticker_id #???
                else:
                    ticker_type = ticker_type['ticker_type']
                    if ticker_type == '上市':
                        ticker_quote = ticker_id + '.tw'
                    else:
                        ticker_quote = ticker_id + '.two'
                ticker_dict[ticker_quote] = ticker_id
                task_list.append(
                    self.quote_price_core(ticker_quote, \
                                          start_date, \
                                          end_date, \
                                          logger, \
                                          refresh, \
                                          retry)
                )
                
        if len(task_list) > 0:
            task_result = asyncio.run(self.quote_price_start(task_list))
            for task_data in task_result:
                ticker_quote, frame_data = task_data
                if dump == "csv":
                    output_name = self.out_path + "{}_daily_price.csv".format(ticker_id)
                elif dump == "xlsx":
                    output_name = self.out_path + "{}_daily_price.xlsx".format(ticker_id)

                if output_name.endswith('csv'):
                    frame_data.to_csv(output_name, encoding = 'cp950')
                elif output_name.endswith('xlsx'):
                    frame_data.to_excel(output_name)
                frame_dict[ticker_dict.get(ticker_quote)] = frame_data
            return frame_dict
        elif len(frame_dict) > 0:
            return frame_dict
        else:
            return None
            
if __name__ == "__main__":
    ticker_list = TickerList().quote_ticker_list(logging.getLogger(), refresh = True)
    if ticker_list is None:
        pass
    else:
        ticker_list = list(ticker_list.index)
        scraper = DailyPrice()
        scraper.quote_daily_price(ticker_list, '2005-01-01', '2019-08-02', \
            logging.getLogger(), refresh = True, dump = "csv")
        scraper.quote_daily_price(ticker_list, '2005-01-01', '2019-08-02', \
            logging.getLogger(), refresh = False, dump = "csv")