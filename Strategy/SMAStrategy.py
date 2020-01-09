import numpy as numpy
from Quant.TradeStrategy import *
from Plotter.LinePlot import *

class SMAStrategy(TradeStrategy):
    def __init__(self, trade_name, trade_config):
        # Initialize super class
        super().__init__(
            trade_name,
            trade_config
        )
 
        self.operation   = LinePlot('Trade', self.out_folder)
        self.equity_all  = LinePlot('Equity', self.out_folder)

    def quote(self, event):
        ticker_id   = self.ticker_list[0]
        event_time  = event.time
        event_data  = event.data[ticker_id]
        price_val   = event_data['close'][-1]
        bband_upper = event_data['SMA5'][-1]
        bband_lower = event_data['SMA15'][-1]
        buy_price   = numpy.nan
        sell_price  = numpy.nan
    
        #if slowk_val < 10 or slowd_val < 10:
        #    self.log_handler.debug('buy@{} ${}'.format(event_time.strftime('%Y-%m-%d'), price_val))
        #    buy_price = price_val
        #    self.buy(ticker_id, 1000, buy_price)
        #elif slowk_val > 90 or slowd_val > 90:
        #    self.log_handler.debug('sell@{} ${}'.format(event_time.strftime('%Y-%m-%d'), price_val))
        #    sell_price = price_val
        #    self.sell(ticker_id, 1000, sell_price)
        #else:
        #    #Do Nothing
        #    pass

        self.operation.add({'time': event.event_time, 
                            ticker_id: price_val,
                            'buy': buy_price,
                            'sell': sell_price})
        
        self.equity_all.add({"time": event.event_time,
                             "equity": self.trade_broker.equity()})

    def term(self, event):
        self.operation.plot(x_axis = 'time',
                            color = ['b', 'r', 'g'],
                            style = ['-', 'None', 'None'],
                            marker = ['None', '^', '^'])

        self.equity_all.plot(x_axis = 'time',
                             color = ['b'],
                             style = ['-'],
                             marker = ['None'])
