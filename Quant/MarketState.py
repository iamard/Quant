import datetime as datetime
from .TimeManager import *
from .EventType import *
from .EventQueue import *

class MarketState(EventQueue):
    MARKET_OPEN  = EventBase.OPEN_EVENT
    MARKET_CLOSE = EventBase.CLOSE_EVENT

    def __init__(self, time_beat, log_handler):
        EventQueue.__init__(self, log_handler)

        self.time_beat  = time_beat
        self.timer_lock = None
        self.timer_list = []

    def __time__(self, time):    
        if time.hour   == 8 and \
           time.minute == 0:
            self.submit(OpenEvent(time))
        elif time.hour   == 16 and \
             time.minute == 0:
            self.submit(CloseEvent(time))

    def setup(self):
        self.timer_lock = threading.RLock()
            
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