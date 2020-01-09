import datetime as datetime
from .TimeManager import *
from .EventType import *
from .EventQueue import *

class MarketState:
    MARKET_OPEN  = EventBase.OPEN_EVENT
    MARKET_CLOSE = EventBase.CLOSE_EVENT

    def __init__(self, time_beat, data_source, log_handler):
        self.time_beat   = time_beat
        self.data_source = data_source
        self.event_queue = None
        self.timer_lock  = None
        self.timer_list  = []
        self.log_handler = log_handler

    def __time__(self, time):
        curr_date = time.date()
        if self.data_source.trade(curr_date) == False:
            self.log_handler.info('Not a trading date', curr_date)
            return
    
        if time.hour   == 8 and \
           time.minute == 0:
            self.event_queue.submit(OpenEvent(time))
        elif time.hour   == 16 and \
             time.minute == 0:
            self.event_queue.submit(CloseEvent(time))

    def attach(self, event_type, observer):
        if event_type == self.MARKET_OPEN or \
           event_type == self.MARKET_CLOSE:
            self.event_queue.attach(event_type, observer)

    def detach(self, event_type, observer):
        if event_type == self.MARKET_OPEN or \
           event_type == self.MARKET_CLOSE:
            self.event_queue.detach(event_type, observer)
            
    def setup(self):
        self.event_queue = EventQueue(self.log_handler)
        self.timer_lock  = threading.RLock()

    def start(self):
        curr_time = self.time_beat.time()
        open_time = datetime.datetime(year = curr_time.year,
                                      month = curr_time.month,
                                      day = curr_time.day,
                                      hour = 8)
        if open_time < curr_time:
            open_time += datetime.timedelta(days = 1)

        close_time  = datetime.datetime(year = curr_time.year,
                                        month = curr_time.month,
                                        day = curr_time.day,
                                        hour = 16)
        if close_time < curr_time:
            close_time += datetime.timedelta(days = 1)
    
        open_timer = self.time_beat.attach(open_time,
                                           datetime.timedelta(days = 1), 
                                           self.__time__)
        close_timer = self.time_beat.attach(close_time, 
                                            datetime.timedelta(days = 1), 
                                            self.__time__)

        self.timer_lock.acquire()                                       
        self.timer_list.append(open_timer)
        self.timer_list.append(close_timer)
        self.timer_lock.release()

    def stop(self):
        for timer in self.timer_list:
            self.time_beat.detach(timer)
        
        self.timer_lock.acquire()
        self.timer_list.clear()
        self.timer_lock.release()

    def free(self):
        pass