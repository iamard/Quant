import threading as threading
import datetime as datetime
from .DataFeed import *
from .EventQueue import *
from .EventType import *
from .Portfolio import *

class DataSource(PriceQuoter):
    def __init__(self, time_beat, signal_dict, look_back, log_handler):
        # Initialize parent class
        super().__init__()

        self.time_beat  = time_beat
        self.price_data = {}
        self.data_feed  = DataFeedFactory.create(
            signal_dict,
            self.time_beat.base() - datetime.timedelta(days = look_back + 30),
            time_beat.end(),
            log_handler)
        self.log_handler = log_handler

    def is_tick(self):
        return False

    def quote(self, ticker_list):
        quote_list = []
        for ticker_id in ticker_list:
            price_data = self.price_data.get(ticker_id, None)
            if price_data is None:
                quote_list.append(ticker_id)

        if len(quote_list) > 0:
            price_data = self.data_feed.quote(quote_list)
            self.price_data.update(price_data)
           
        price_data = {}
        for ticker_id in ticker_list:
            price_data[ticker_id] = self.price_data.get(ticker_id, None)
            if price_data is None:
                return None

        return price_data

    def __query__(self, ticker_id):
        price_data = self.quote([ticker_id])[ticker_id]
        curr_date  = self.time_beat.time().date()
        price_data = price_data.iloc[price_data.index.get_loc(curr_date, 
                                                              method = 'nearest')]
        return price_data

    def close(self, ticker_id):
        price_data  = self.__query__(ticker_id)
        return price_data['close']

    def low(self, ticker_id):
        price_data  = self.__query__(ticker_id)
        return price_data['low']

    def high(self, ticker_id):
        price_data  = self.__query__(ticker_id)
        return price_data['low']

class TradeBroker:
    BAR_DATA = EventBase.BAR_EVENT

    def __init__(self, time_beat, start_cash, signal_dict, look_back, log_handler):    
        self.time_beat   = time_beat
        self.data_quoter = DataSource(time_beat,
                                      signal_dict,
                                      look_back, 
                                      log_handler)
        self.portfolio   = Portfolio(self.data_quoter,
                                     start_cash, 
                                     log_handler)
        self.look_back   = look_back
        self.event_queue = None
        self.timer_lock  = None
        self.quote_timer = None
        self.attach_list = []
        self.log_handler = log_handler

    def buy(self, ticker_id, quantity, price):
        if price < self.data_quoter.low(ticker_id):
            return
    
        return self.portfolio.transact(Portfolio.ACTION_BUY,
                                       ticker_id,
                                       quantity,
                                       price,
                                       (quantity * price) * 0.001)
    
    def sell(self, ticker_id, quantity, price):
        if price > self.data_quoter.high(ticker_id):
            return
    
        return self.portfolio.transact(Portfolio.ACTION_SELL,
                                       ticker_id,
                                       quantity,
                                       price,
                                       (quantity * price) * 0.001)

    def quantity(self, ticker_id):
        return self.portfolio.quantity(ticker_id)

    def update(self):
        return self.portfolio.update()   

    def cash(self):
        return self.portfolio.cash()

    def equity(self):
        return self.portfolio.equity()

    def __time__(self, time):
        start_date = (time - datetime.timedelta(days = self.look_back + 30)).date()
        end_date   = time.date()
        
        ticker_data = self.data_quoter.quote(self.attach_list)
        if ticker_data is None:
            self.log_handler.error('No available price data!')
            return None
        
        self.log_handler.debug('trade@', end_date)
        
        event_data = {}
        for ticker_id in self.attach_list:
            try:
                price_data = ticker_data[ticker_id]
                end_index  = price_data.index.get_loc(end_date)
                price_data = price_data.iloc[end_index - self.look_back: end_index]
                if price_data.empty == True:
                    self.log_handler.info('Empty price data frame!')
                    return
            except KeyError:
                # Should not a trade date
                return

            event_data[ticker_id] = price_data
        
        if len(event_data) > 0:
            self.event_queue.submit(BarEvent(time, event_data))

    def attach(self, event_type, ticker_list, observer):
        if event_type == self.BAR_DATA:
            price_data = self.data_quoter.quote(ticker_list)
            if price_data is None:
                return False

            self.event_queue.attach(event_type, observer)
            self.attach_list.extend(ticker_list)
        return True

    def setup(self):
        self.event_queue = EventQueue(self.log_handler)
        self.timer_lock  = threading.RLock()
        self.quote_timer = None

    def start(self):
        curr_time  = self.time_beat.time()
        quote_time = datetime.datetime(year = curr_time.year,
                                       month = curr_time.month,
                                       day = curr_time.day,
                                       hour = 8)
        if quote_time < curr_time:
            quote_time += datetime.timedelta(days = 1)
                                       
        self.timer_lock.acquire()
        self.quote_timer = self.time_beat.attach(quote_time,
                                                 datetime.timedelta(days = 1), 
                                                 self.__time__)
        self.timer_lock.release()

    def stop(self):
        self.timer_lock.acquire()
        if self.quote_timer is not None:
            self.time_beat.detach(self.quote_timer)
            self.quote_timer = None
        self.timer_lock.release()

    def free(self):
        pass
