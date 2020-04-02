from Quant.TradeStrategy import *

class StochStrategy(TradeStrategy):
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
        slowk_val  = event_data['slowk'][-1]
        slowd_val  = event_data['slowd'][-1]
    
        if slowk_val < 10 or slowd_val < 10:
            self.log_handler.debug('buy@{} ${}'.format(event_time.strftime('%Y-%m-%d'), price_val))
            self.buy(ticker_id, 1000, price_val)
        elif slowk_val > 90 or slowd_val > 90:
            self.log_handler.debug('sell@{} ${}'.format(event_time.strftime('%Y-%m-%d'), price_val))
            self.sell(ticker_id, 1000, price_val)
