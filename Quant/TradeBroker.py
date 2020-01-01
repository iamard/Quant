from .Portfolio import *

class PriceHandler(PriceQuoter):
        def __init__(self, beat_timer, log_handler):
            super().__init__()

            self.beat_timer  = beat_timer
            self.data_quoter = DataQuoter(log_handler)
            self.price_data  = {}

        def is_tick(self):
            return False

        def quote(self, ticker_id):
            price_data = self.price_data.get(ticker_id, None)
            if price_data is None:
                price_data = self.data_quoter.price(
                    ticker_id,
                    self.beat_timer.base(),
                    self.beat_timer.end()
                )
                self.price_data[ticker_id] = price_data[ticker_id]
                price_data = price_data[ticker_id]

            return price_data
            
        def close(self, ticker_id):
            price_data  = self.quote(ticker_id)  
            curr_date   = self.beat_timer.time()
            price_value = price_data.iloc[price_data.index.get_loc(curr_date, method = 'nearest')]
            return price_value['close']

        def low(self, ticker_id):
            price_data = self.quote(ticker_id)  
            curr_date  = self.beat_timer.time().date()
            price_value = price_data.iloc[price_data.index.get_loc(curr_date, method = 'nearest')]
            return price_value['low']
            
class TradeBroker:
    def __init__(self, beat_timer, start_cash, log_handler):
        self.beat_timer   = beat_timer
        self.portfolio    = Portfolio(PriceHandler(beat_timer, log_handler), 
                                      start_cash, 
                                      log_handler)
        self.log_handler  = log_handler

    def buy(self, ticker, quantity, price):
        return self.portfolio.transact(Portfolio.ACTION_BUY,
                                       ticker,
                                       quantity,
                                       price,
                                       (quantity * price) * 0.001)
    
    def sell(self, ticker, quantity, price):
        return self.portfolio.transact(Portfolio.ACTION_SELL,
                                       ticker,
                                       quantity,
                                       price,
                                       (quantity * price) * 0.001)

    def quantity(self, ticker):
        return self.portfolio.quantity(ticker)

    def update(self):
        return self.portfolio.update()   

    def cash(self):
        return self.portfolio.cash()

    def equity(self):
        return self.portfolio.equity()
