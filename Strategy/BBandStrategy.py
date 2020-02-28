import numpy as numpy
from Quant.TradeStrategy import *
from Plotter.LinePlot import *

class BBandStrategy(TradeStrategy):
    def __init__(self, trade_name, trade_config):
        # Initialize super class
        super().__init__(
            trade_name,
            trade_config
        )
 
        self.operation = LinePlot('Trade', self.out_folder)

    def quote(self, event):
        ticker_id   = self.ticker_list[0]
        event_time  = event.time
        event_data  = event.data[ticker_id]
        price_val   = event_data['close'][-1]
        bband_upper = event_data['bband-upper'][-1]
        bband_lower = event_data['bband-lower'][-1]
        buy_price   = numpy.nan
        sell_price  = numpy.nan
    
        if price_val < bband_lower:
            self.log_handler.debug('buy@{} ${}'.format(event_time.strftime('%Y-%m-%d'), price_val))
            buy_price = price_val
            self.buy(ticker_id, 1000, buy_price)
        elif price_val > bband_upper:
            self.log_handler.debug('sell@{} ${}'.format(event_time.strftime('%Y-%m-%d'), price_val))
            sell_price = price_val
            self.sell(ticker_id, 1000, sell_price)
        else:
            # Do Nothing
            pass

        self.operation.add({'time': event.event_time, 
                            ticker_id: price_val,
                            'buy': buy_price,
                            'sell': sell_price})

    def term(self, event):
        self.operation.plot(title = 'test',
                            x_axis = 'time',
                            color = ['b', 'r', 'g'],
                            style = ['-', 'None', 'None'],
                            marker = ['None', '^', '^'])
