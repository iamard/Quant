from Quant.TradeStrategy import *

class BBandStrategy(TradeStrategy):
    def __init__(self, trade_name, trade_config):
        # Initialize super class
        super().__init__(
            trade_name,
            trade_config
        )

    def quote(self, event):
        ticker_id   = self.ticker_list[0]
        event_time  = event.time
        event_data  = event.data[ticker_id]
        price_val   = event_data['close'][-1]
        bband_upper = event_data['bband-upper'][-1]
        bband_lower = event_data['bband-lower'][-1]
    
        if price_val < bband_lower:
            self.log_handler.debug('buy@{} ${}'.format(event_time.strftime('%Y-%m-%d'), price_val))
            self.buy(ticker_id, 1000, price_val)
        elif price_val > bband_upper:
            self.log_handler.debug('sell@{} ${}'.format(event_time.strftime('%Y-%m-%d'), price_val))
            self.sell(ticker_id, 1000, price_val)
