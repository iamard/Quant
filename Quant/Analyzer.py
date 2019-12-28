from datetime import timedelta
from DataQuoter import *
import talib as talib
import pandas as pandas

class BaseAnalyzer:
    def __init__(self, ticker_list, start_date, end_date, log_handler):
        self.ticker_list = ticker_list
        self.log_handler = log_handler
        self.data_quoter = DataQuoter(ticker_list, log_handler)
        self.start_date  = start_date - timedelta(50)
        self.end_date    = end_date

    def calc_technical_index(self):
        frame = self.data_quoter.quote_history_price(self.start_date, \
                                                     self.end_date)
        if frame is None:
            return None
        return frame

class AnalyzerDecorator:
    def __init__(self, strategy):
      self.decorated = strategy 

    def calc_technical_core(self):
        pass
      
    def calc_technical_index(self):
        frame  = self.decorated.calc_technical_index()
        output = {}
        for key, data in frame.items():
            extra = self.calc_technical_core(frame[key])
            extra = pandas.concat([frame[key], extra], axis = 1, sort = False)

            # Save the augmented frame
            output[key] = extra

        return output
            
class SMAAnalyzer(AnalyzerDecorator):
    def __init__(self, previous, periods = [5, 15, 19, 21, 25, 30]):
        super().__init__(previous)
        self.periods = periods

    def calc_technical_core(self, frame):
        output = {}
        for period in self.periods:
            output['SMA' + str(period)] = talib.MA(frame['adj_close'], period)
        output = pandas.DataFrame(output, index = frame.index)
        return output

class MACDAnalyzer(AnalyzerDecorator):
    def __init__(self, previous, options = {'fast_period': 12, 
            'slow_period': 26, 'signal_period': 9}):
        super().__init__(previous)
        self.options = options

    def calc_technical_core(self, frame):
        dif, dea, macd = talib.MACD(frame['adj_close'], \
                                    fastperiod = self.options['fast_period'], \
                                    slowperiod = self.options['slow_period'], \
                                    signalperiod = self.options['signal_period'])
        output = pandas.DataFrame({ 'MACD': macd, 'DIF': dif, 'DEA': dea }, \
                index = frame.index)
        return output

class STOCHAnalyzer(AnalyzerDecorator):
    def __init__(self, previous, options = {'fastk_period': 9, 
            'slowk_period': 3, 'slowd_period': 3}):
        super().__init__(previous)
        self.options = options

    def calc_technical_core(self, frame):
        slowk, slowd = talib.STOCH(frame['high'], \
                                   frame['low'], \
                                   frame['close'], \
                                   fastk_period = self.options['fastk_period'], \
                                   slowk_period = self.options['slowk_period'], \
                                   slowk_matype = 0, \
                                   slowd_period = self.options['slowd_period'], \
                                   slowd_matype = 0)
        output = pandas.DataFrame({ 'slowk': slowk, 'slowd': slowd}, \
                index = frame.index)
        return output

class BBANDAnalyzer(AnalyzerDecorator):
    def __init__(self, previous, options = {'time_period': 10, 
            'nbdevup': 2, 'nbdevdn': 2}):
        super().__init__(previous)
        self.options = options

    def calc_technical_core(self, frame):
        upper, middle, lower = talib.BBANDS(frame['adj_close'], 
                                            timeperiod = self.options['time_period'],
                                            nbdevup = self.options['nbdevup'],
                                            nbdevdn = self.options['nbdevdn'],
                                            matype = 0)
        bbp = (frame['adj_close'] - lower) / (upper - lower)
        
        output = pandas.DataFrame({ 'bband-bbp': bbp,
                                    'bband-upper': upper, \
                                    'bband-middle': middle, \
                                    'bband-lower': lower }, \
                                  index = frame.index)
        return output

class AnalyzerFactory():
    @classmethod
    def create_analyzer(self, option_dict, ticker_list, start_date, end_date, log_handler):
        analyzer = BaseAnalyzer(ticker_list, start_date, end_date, log_handler)
        if option_dict.get('sma') != None:
            analyzer = SMAAnalyzer(analyzer, option_dict.get('sma'))
        if option_dict.get('macd') != None:
            analyzer = MACDAnalyzer(analyzer, option_dict.get('macd'))
        if option_dict.get('stoch') != None:
            analyzer = STOCHAnalyzer(analyzer, option_dict.get('stoch'))
        if option_dict.get('bband') != None:
            analyzer = BBANDAnalyzer(analyzer, option_dict.get('bband'))
        return analyzer
