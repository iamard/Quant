# coding=utf-8

from ConfigParser import *
from Crawler import *
from Database import *
from datetime import *
from dateutil import *
import threading
import time
from collections import namedtuple

class DataManager:
    def __init__(self):
        # Create configuration handle
        self.__config  = ConfigParser()
        self.__config.read('Config.ini')

    def _quote_daily_trade(self, date_range, code_list, dump = None, if_exists = 'fail'):
        column_list = ['Date'] + code_list

        # For daily volume
        daily_vol   = pd.DataFrame(columns = column_list)
        daily_vol['Date'] = date_range
        daily_vol   = daily_vol.set_index('Date')
        
        # For daily open price
        daily_open  = pd.DataFrame(columns = column_list)
        daily_open['Date'] = date_range
        daily_open  = daily_open.set_index('Date')

        # For daily high price
        daily_high = pd.DataFrame(columns = column_list)
        daily_high['Date'] = date_range
        daily_high = daily_high.set_index('Date')

        # For daily low price
        daily_low   = pd.DataFrame(columns = column_list)
        daily_low['Date'] = date_range
        daily_low   = daily_low.set_index('Date')

        # For daily close price
        daily_close = pd.DataFrame(columns = column_list)
        daily_close['Date'] = date_range
        daily_close = daily_close.set_index('Date')

        daily_trade = DailyTrade()
        
        # Fetch daily trade information
        month_range = [day.date() for day in rrule.rrule(rrule.MONTHLY, dtstart = date_range[0], until = date_range[-1])]
        for current in month_range:
            for code in code_list:
                print "Quote daily trade " + code + " for "+ str(current.year) + "-" + str(current.month)
                daily_price = daily_trade.quote_daily_trade(code, current.year, current.month, dump = 'csv')
                if daily_price is not None:
                    # Save daily volume, open, close, high, and low values
                    volume    = dict(zip(daily_price.index, daily_price[u'成交股數'].values))
                    open_raw  = dict(zip(daily_price.index, daily_price[u'開盤價'].values))
                    high_raw  = dict(zip(daily_price.index, daily_price[u'最高價'].values))
                    low_raw   = dict(zip(daily_price.index, daily_price[u'最低價'].values))
                    close_raw = dict(zip(daily_price.index, daily_price[u'收盤價'].values))
                    for key in daily_price.index:
                        # Store daily volume
                        daily_vol.loc[datetime.strptime(key, "%Y-%m-%d"), code] = volume[key]
                        
                        # Store daily open price
                        daily_open.loc[datetime.strptime(key, "%Y-%m-%d"), code] = open_raw[key]

                        # Store daily high price
                        daily_high.loc[datetime.strptime(key, "%Y-%m-%d"), code] = high_raw[key]

                        # Store daily low price
                        daily_low.loc[datetime.strptime(key, "%Y-%m-%d"), code] = low_raw[key]

                        # Store daily close price
                        daily_close.loc[datetime.strptime(key, "%Y-%m-%d"), code] = close_raw[key]
                                
                time.sleep(5)

        daily_vol   = daily_vol.dropna(how = 'all')
        daily_open  = daily_open.dropna(how = 'all')
        daily_high  = daily_high.dropna(how = 'all')
        daily_low   = daily_low.dropna(how = 'all')
        daily_close = daily_close.dropna(how = 'all')

        if dump == "csv":
            daily_vol.to_csv("daily_vol.csv", encoding = 'cp950')
            daily_open.to_csv("daily_open.csv", encoding = 'cp950')
            daily_high.to_csv("daily_high.csv", encoding = 'cp950')
            daily_low.to_csv("daily_low.csv", encoding = 'cp950')
            daily_close.to_csv("daily_close.csv", encoding = 'cp950')
        elif dump == "xlsx":
            daily_vol.to_excel("daily_vol.xlsx")
            daily_open.to_excel("daily_open.xlsx")
            daily_high.to_excel("daily_high.xlsx")
            daily_low.to_excel("daily_low.xlsx")
            daily_close.to_excel("daily_close.xlsx")

        # Create database handle
        database = Database()
            
        if len(daily_vol.index) != 0:
            database.write_data_frame(daily_vol, "daily_vol", index = True, if_exists = if_exists)

        if len(daily_open.index) != 0:
            database.write_data_frame(daily_open, "daily_open", index = True, if_exists = if_exists)

        if len(daily_high.index) != 0:
            database.write_data_frame(daily_high, "daily_high", index = True, if_exists = if_exists)

        if len(daily_low.index) != 0:
            database.write_data_frame(daily_low, "daily_low", index = True, if_exists = if_exists)

        if len(daily_close.index) != 0:
            database.write_data_frame(daily_close, "daily_close", index = True, if_exists = if_exists)

    def _quote_daily_info(self, date_range, code_list, dump = None, if_exists = 'fail'):
        column_list = ['Date'] + code_list

        # For daily PBR ratio
        daily_pbr   = pd.DataFrame(columns = column_list)
        daily_pbr['Date'] = date_range
        daily_pbr   = daily_pbr.set_index('Date')

        # For daily yield ratio
        daily_yield = pd.DataFrame(columns = column_list)
        daily_yield['Date'] = date_range
        daily_yield = daily_yield.set_index('Date')

        # For daiy PE ratio
        daily_pe    = pd.DataFrame(columns = column_list)
        daily_pe['Date'] = date_range
        daily_pe    = daily_pe.set_index('Date')

        daily_info  = DailyInfo()
        date_list   = date_range.tolist()
        for current in date_list:
            print "Quote daily info for " + current.strftime('%Y-%m-%d')

            # Quote daily PBR, yield and PE value
            daily_value = daily_info.quote_daily_info(current.year, current.month, current.day)
            if daily_value is not None:
                # Daily PBR ratio
                pbr_raw   = dict(zip(daily_value.index, daily_value['股價淨值比'].values))
                for key in pbr_raw.keys():
                    daily_pbr.loc[current.strftime('%Y-%m-%d'), key] = pbr_raw[key]

                # Daily yield ratio
                yield_raw = dict(zip(daily_value.index, daily_value['殖利率(%)'].values))
                for key in yield_raw.keys():
                    daily_yield.loc[current.strftime('%Y-%m-%d'), key] = yield_raw[key]

                # Daily PE ratio
                pe_raw    = dict(zip(daily_value.index, daily_value['本益比'].values))
                for key in pe_raw.keys():
                    daily_pe.loc[current.strftime('%Y-%m-%d'), key] = pe_raw[key]

            time.sleep(5)

        daily_pbr   = daily_pbr.dropna(how = 'all')
        daily_yield = daily_yield.dropna(how = 'all')
        daily_pe    = daily_pe.dropna(how = 'all')

        daily_pbr   = daily_pbr.apply(pd.to_numeric, errors = 'coerce')
        daily_yield = daily_yield.apply(pd.to_numeric, errors = 'coerce')
        daily_pe    = daily_pe.apply(pd.to_numeric, errors = 'coerce')

        if dump == "csv":
            daily_pbr.to_csv("daily_pbr.csv", encoding = 'cp950')
            daily_yield.to_csv("daily_yield.csv", encoding = 'cp950')
            daily_pe.to_csv("daily_pe.csv", encoding = 'cp950')
        elif dump == "xlsx":
            daily_pbr.to_excel("daily_pbr.xlsx")
            daily_yield.to_excel("daily_yield.xlsx")
            daily_pe.to_excel("daily_pe.xlsx")

        # Create database handle
        database = Database()
            
        if len(daily_pbr.index) != 0:
            database.write_data_frame(daily_pbr, "daily_pbr", index = True, if_exists = if_exists)

        if len(daily_yield.index) != 0:
            database.write_data_frame(daily_yield, "daily_yield", index = True, if_exists = if_exists)

        if len(daily_pe.index) != 0:
            database.write_data_frame(daily_pe, "daily_pe", index = True, if_exists = if_exists)

    def _quote_web_data(self, start_date, end_date, dump = None, if_exists = 'fail'):
        stock_code  = StockCode()       
        stock_frame = stock_code.quote_stock_code(dump = None)
        code_list   = list(stock_frame.index.values)
        date_range  = pd.DatetimeIndex(pd.date_range(start_date, end_date)).date
        thread_list = []

        thread_list.append(threading.Thread(
                target = self._quote_daily_trade, args = [date_range, code_list]))

        thread_list.append(threading.Thread(
                target = self._quote_daily_info, args = [date_range, code_list]))
                
        for thread in thread_list:
            thread.start()

        for thread in thread_list:
            thread.join()

    def _quote_database(self, start_date, end_date):
        database    = Database()
        daily_vol   = database.read_data_frame("daily_vol")
        daily_open  = database.read_data_frame("daily_open")
        daily_high  = database.read_data_frame("daily_high")
        daily_low   = database.read_data_frame("daily_low")
        daily_close = database.read_data_frame("daily_close")
        daily_pbr   = database.read_data_frame("daily_pbr")
        daily_yield = database.read_data_frame("daily_yield")
        daily_pe    = database.read_data_frame("daily_pe")

        output_data = {"daily_vol": daily_vol,
                       "daily_open": daily_open,
                       "daily_high": daily_high,
                       "daily_low": daily_low,
                       "daily_close": daily_close,
                       "daily_pbr": daily_pbr,
                       "daily_yield": daily_yield,
                       "daily_pe": daily_pe}

        return output_data

    def quote_stock_data(self, start_date, end_date):
        config      = self.__config
        valid_start = config.get("DATABASE", "validStart")
        if valid_start != '':
            print valid_start
            valid_start = datetime.strptime(valid_start, "%Y-%m-%d")
        else:
            valid_start = None
        
        valid_end   = config.get("DATABASE", "validEnd")
        if valid_end != '':
            valid_end = datetime.strptime(valid_end, "%Y-%m-%d")
        else:
            valid_end = None

        if valid_start != None and valid_end != None:
            if valid_start > valid_end:
                valid_start = None
                valid_end   = None
            
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date   = datetime.strptime(end_date, "%Y-%m-%d")
        if valid_start == None or valid_end == None:
            self._quote_web_data(start_date, end_date, dump = 'csv', if_exists = "replace")
            config.set("DATABASE", "validStart", start_date.strftime("%Y-%m-%d"))
            config.set("DATABASE", "validEnd", end_date.strftime("%Y-%m-%d"))
        else:
            Range     = namedtuple('Range', ['start', 'end'])
            range1    = Range(start = start_date, end = end_date)
            range2    = Range(start = valid_start, end = valid_end)
            max_start = max(range1.start, range2.start)
            min_end   = min(range1.end, range2.end)
            overlap   = (min_end - max_start).days + 1
            if overlap > 0:
                if start_date < valid_start:
                    if end_date <= valid_end:
                        end_date   = valid_start - timedelta(1)
                        self._quote_web_data(start_date, end_date, if_exists = "append", dump = 'csv')
                    else:
                        # Subrange1
                        period_end = valid_start - timedelta(1)
                        self._quote_web_data(start_date, period_end, if_exists = "append", dump = 'csv')

                        # Subrange2
                        start_date = valid_end + timedelta(1)
                        self._quote_web_data(start_date, end_date, if_exists = "append", dump = 'csv')
                elif end_date > valid_end:
                    start_date = valid_end + timedelta(1)
                    self._quote_web_data(start_date, end_date, if_exists = "append", dump = 'csv')
            else:
                if end_date < valid_start:
                    end_date = valid_start - timedelta(1)
                    self._quote_web_data(start_date, end_date, if_exists = "append", dump = 'csv')
                else:
                    start_date = valid_end + timedelta(1)
                    self._quote_web_data(start_date, end_date, if_exists = "append", dump = 'csv')

            min_start = min(range1.start, range2.start)
            print min_start, start_date
            max_end   = max(range1.end, range2.end)
            config.set("DATABASE", "validStart", min_start.strftime("%Y-%m-%d"))
            config.set("DATABASE", "validEnd", max_end.strftime("%Y-%m-%d"))

        with open('Config.ini', 'wb') as output:
            config.write(output)

        # Read historical data from database
        return self._quote_database(start_date, end_date)

if __name__ == "__main__":
    manager = DataManager()
    manager.quote_stock_data("2013-01-01", "2013-02-03")
