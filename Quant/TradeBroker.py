from .Portfolio import *

class PriceHandler(PriceQuoter):
        def __init__(self, beat_timer, log_handler):
            super().__init__()

            self.beat_timer  = beat_timer
            self.data_quoter = DataQuoter(log_handler)

        def is_tick(self):
            return False

        def last_close(self):
            curr_time  = beat_timer.time()
            price_data = self.data_quoter.price(ticker, curr_time, curr_time)
            return price_data['close']

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
        return self.portfolio.tranact(Portfolio.ACTION_SLD,
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
