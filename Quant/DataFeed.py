from datetime import timedelta
import talib as talib
import numpy as numpy
import pandas as pandas
from Scraper.DataQuoter import *

class DataFeed:
    def __init__(self, log_handler):
        self.data_quoter = DataQuoter(log_handler)
        self.price_data  = {}
        self.log_handler = log_handler

    def quote(self, ticker_list, start_date, end_date):
        quote_list = []
        for ticker_id in ticker_list:
            price_data = self.price_data.get(ticker_id, None)
            if price_data is None:
                quote_list.append(ticker_id)

        if len(quote_list) > 0:
            price_data = self.data_quoter.price(ticker_list,
                                                start_date,
                                                end_date)
            if price_data is None:
                return None
            self.price_data.update(price_data)
           
        price_data = {}
        for ticker_id in ticker_list:
            price_data[ticker_id] = self.price_data.get(ticker_id, None)
            if price_data is None:
                return None

        return price_data
        
class DataDecorator:
    def __init__(self, previous):
      self.decorated = previous 

    def signal(self):
        pass
      
    def quote(self, ticker_list, start_date, end_date):
        frame  = self.decorated.quote(ticker_list, start_date, end_date)
        output = {}
        for key, data in frame.items():
            extra = self.signal(frame[key])
            extra = pandas.concat([frame[key], extra], axis = 1, sort = False)

            # Save the augmented frame
            output[key] = extra

        return output
            
class SMADataFeed(DataDecorator):
    def __init__(self, previous, periods = [5, 15, 19, 21, 25, 30]):
        super().__init__(previous)
        self.periods = periods

    def signal(self, frame):
        output = {}
        for period in self.periods:
            output['SMA' + str(period)] = talib.MA(frame['adj_close'], period)
        output = pandas.DataFrame(output, index = frame.index)

        return output

class MACDDataFeed(DataDecorator):
    def __init__(self, previous, options = {'fast_period': 12, 
            'slow_period': 26, 'signal_period': 9}):
        super().__init__(previous)
        self.options = options

    def signal(self, frame):
        dif, dea, macd = talib.MACD(frame['adj_close'],
                                    fastperiod = self.options['fast_period'],
                                    slowperiod = self.options['slow_period'],
                                    signalperiod = self.options['signal_period'])
        output = pandas.DataFrame({ 'MACD': macd, 'DIF': dif, 'DEA': dea },
                index = frame.index)

        return output

class STOCHDataFeed(DataDecorator):
    def __init__(self, previous, options = {'fastk_period': 9, 
            'slowk_period': 3, 'slowd_period': 3}):
        super().__init__(previous)
        self.options = options

    def signal(self, frame):
        slowk, slowd = talib.STOCH(frame['high'],
                                   frame['low'],
                                   frame['close'],
                                   fastk_period = self.options['fastk_period'],
                                   slowk_period = self.options['slowk_period'],
                                   slowk_matype = 0,
                                   slowd_period = self.options['slowd_period'],
                                   slowd_matype = 0)
        output = pandas.DataFrame({ 'slowk': slowk, 'slowd': slowd},
                index = frame.index)

        return output

class BBandDataFeed(DataDecorator):
    def __init__(self, previous, options = {'time_period': 10, 
            'nbdevup': 2, 'nbdevdn': 2}):
        super().__init__(previous)
        self.options = options

    def signal(self, frame):
        upper, middle, lower = talib.BBANDS(frame['adj_close'], 
                                            timeperiod = self.options['time_period'],
                                            nbdevup = self.options['nbdevup'],
                                            nbdevdn = self.options['nbdevdn'],
                                            matype = 0)
        bbp = (frame['adj_close'] - lower) / (upper - lower)
        
        output = pandas.DataFrame({ 'bband-bbp': bbp,
                                    'bband-upper': upper,
                                    'bband-middle': middle,
                                    'bband-lower': lower },
                                  index = frame.index)
        return output

class RSIDataFeed(DataDecorator):
    def __init__(self, previous, periods = [6, 24]):
        super().__init__(previous)
        self.periods = periods

    def signal(self, frame):
        output = {}
        for period in self.periods:
            output['RSI' + str(period)] = talib.RSI(frame['adj_close'], period)
        output = pandas.DataFrame(output, index = frame.index)
        return output

class ATRDataFeed(DataDecorator):
    def __init__(self, previous, period = 14):
        super().__init__(previous)
        self.period = period

    def signal(self, frame):
        output = {}
        output['ATR' + str(self.period)] = numpy.array(
            talib.ATR(frame['high'].values,
                      frame['low'].values, 
                      frame['close'].values,
                      timeperiod = self.period)
        )
        output = pandas.DataFrame(output, index = frame.index)
        return output

class DataFeedFactory():
    @classmethod
    def create(self, option_dict, log_handler):
        data_feed = DataFeed(log_handler)
        if option_dict.get('sma', None) is not None:
            data_feed = SMADataFeed(data_feed, option_dict.get('sma'))
        if option_dict.get('macd', None) is not None:
            data_feed = MACDDataFeed(data_feed, option_dict.get('macd'))
        if option_dict.get('stoch', None) is not None:
            data_feed = STOCHDataFeed(data_feed, option_dict.get('stoch'))
        if option_dict.get('bband', None) is not None:
            data_feed = BBandDataFeed(data_feed, option_dict.get('bband'))
        if option_dict.get('rsi', None) is not None:
            data_feed = RSIDataFeed(data_feed, option_dict.get('rsi'))
        if option_dict.get('atr', None) is not None:
            data_feed = ATRDataFeed(data_feed, option_dict.get('atr'))
        return data_feed
