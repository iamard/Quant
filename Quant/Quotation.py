import threading as threading
from Scraper.DataQuoter import *
from .EventQueue import *
from .EventType import *
import datetime as datetime

class Quotation(EventQueue):
    BAR_DATA = EventBase.BAR_EVENT

    def __init__(self, time_beat, ticker_list, look_back, log_handler):
        EventQueue.__init__(self, log_handler)
    
        self.time_beat   = time_beat
        self.data_quoter = DataQuoter(log_handler)
        self.price_frame = self.data_quoter.price(
            ticker_list, 
            time_beat.base() - datetime.timedelta(days = look_back + 30),  # 30 for margin
            time_beat.end()
        )
        self.ticker_list = ticker_list
        self.look_back   = look_back
        self.timer_lock  = None
        self.quote_timer = None
        
    def __time__(self, time):
        start_date = (time - datetime.timedelta(days = self.look_back + 30)).date()
        end_date   = time.date()

        event_data = {}
        for ticker_id in self.ticker_list:
            frame_data = self.price_frame[ticker_id]
            frame_data = frame_data[(frame_data.index.date > start_date) & \
                                    (frame_data.index.date < end_date)]
            frame_data = frame_data.dropna()
            
            if frame_data.empty == False:
                frame_data = frame_data[-self.look_back:]
                event_data[ticker_id] = frame_data
        
        if len(event_data) > 0:
            self.submit(BarEvent(time, event_data))

    def setup(self):
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
