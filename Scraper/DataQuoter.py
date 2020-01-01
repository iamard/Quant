from .DailyPrice import *

class DataQuoter:
    def __init__(self, log_handler):
        self.log_handler = log_handler
        self.daily_price = DailyPrice()
        
    def price(self, ticker_list, start_time, end_time):
        if isinstance(ticker_list, list) == False:
            ticker_list = [ticker_list]
    
        price_dict = self.daily_price.quote_daily_price(
            ticker_list, start_time, end_time, self.log_handler
        )

        return price_dict
