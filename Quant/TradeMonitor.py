from .TimeManager import *
from .EventType import *
from .EventQueue import *

class TradeMonitor(EventQueue):
    TRADE_START = EventBase.START_EVENT
    TRADE_STOP  = EventBase.STOP_EVENT

    def __init__(self, time_beat, log_handler):
        EventQueue.__init__(self, log_handler)

        self.time_beat  = time_beat
        self.start_time = time_beat.base()
        self.end_time   = time_beat.end()
        self.timer_lock = None
        self.timer_list = []

    def __time__(self, time):
        if time == self.start_time:
            self.submit(StartEvent(time))
        elif time == self.end_time:
            self.submit(StopEvent(time))

    def setup(self):
        self.timer_lock = threading.RLock()
            
    def start(self):
        start_timer = self.time_beat.attach(self.start_time,
                                            None, 
                                            self.__time__)
        end_timer   = self.time_beat.attach(self.end_time,
                                            None, 
                                            self.__time__)

        self.timer_lock.acquire()
        self.timer_list.append(start_timer)
        self.timer_list.append(end_timer)
        self.timer_lock.release()

    def stop(self):
        for timer in self.timer_list:
            self.time_beat.detach(timer)
        
        self.timer_lock.acquire()
        self.timer_list.clear()
        self.timer_lock.release()

    def free(self):
        pass