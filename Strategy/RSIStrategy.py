import numpy as numpy
from Quant.TradeStrategy import *

class RSIStrategy(TradeStrategy):
    def __init__(self, trade_name, trade_config):
        # Initialize super class
        super().__init__(
            trade_name,
            trade_config
        )

    def quote(self, event):
        ticker_id  = self.ticker_list[0]
        event_time = event.time
        event_data = event.data[ticker_id]
        price_val  = event_data['close'][-1]
        prev_rsi6  = event_data['RSI6'][-2]
        prev_rsi24 = event_data['RSI24'][-2]
        curr_rsi6  = event_data['RSI6'][-1]
        curr_rsi24 = event_data['RSI24'][-1]
    
        if curr_rsi6 > curr_rsi24 and prev_rsi6 < prev_rsi24:
            self.log_handler.debug('buy@{} ${}'.format(event_time.strftime('%Y-%m-%d'), price_val))
            self.buy(ticker_id, 1000, price_val)
        elif curr_rsi6 < curr_rsi24 and prev_rsi6 > prev_rsi24:
            self.log_handler.debug('sell@{} ${}'.format(event_time.strftime('%Y-%m-%d'), price_val))
            self.sell(ticker_id, 1000, price_val)
