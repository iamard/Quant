import time as time
import sys as sys
import traceback as traceback
import logging as logging
import threading as threading
import datetime as datetime
from .Singleton import *

class TimerTask:
    def __init__(self, start_time, time_delta, observer):
        self.next_time  = start_time
        self.time_delta = time_delta
        self.observer   = observer

    def is_periodic(self):
        return self.time_delta != None
        
    def advance(self):
        self.next_time = self.next_time + self.time_delta

    def next_moment(self):
        return self.next_time
        
class TimeManager(metaclass = Singleton):
    def __init__(self, cur_strategy, start_time, end_time, log_handler):
        self.cur_strategy  = cur_strategy
        self.start_time    = start_time
        self.current_time  = start_time
        self.end_time      = end_time
        self.log_handler   = log_handler
        self.observer_list = []
        self.stop_event    = None
        self.timer_lock    = None
        self.timer_thread  = None

    def __notify__(self):
        try:
            self.timer_lock.acquire()
            if len(self.observer_list) > 0 and \
               self.current_time >= (self.observer_list[0].next_moment() - 
                                     datetime.timedelta(milliseconds = 1)):
                moment = self.observer_list[0]

                self.log_handler.info(
                    self.current_time.strftime('%Y-%m-%d %H:%M') + 
                    ' @call ' + str(moment.observer)
                )
                moment.observer(self.current_time)
                self.log_handler.info(
                    self.current_time.strftime('%Y-%m-%d %H:%M') + 
                    ' @done ' + str(moment.observer)
                )

                if moment.is_periodic():
                    moment.advance()
                else:
                    self.observer_list = self.observer_list[1:]
        except Exception as exception:
            trace_back = traceback.format_exception(*sys.exc_info())
            self.cur_strategy.notify((exception, trace_back))
        finally:
            self.timer_lock.release()

    def __advance__(self):
        self.timer_lock.acquire()
        if len(self.observer_list) > 0:
            self.observer_list.sort(key = lambda task: task.next_moment())
            self.current_time += (self.observer_list[0].next_moment() - self.current_time)
        self.timer_lock.release()

    def __tick__(self):
        while self.stop_event.is_set() == False:
            self.__notify__()
            self.__advance__()
            time.sleep(0.001)

    def base(self):
        return self.start_time
            
    def time(self):
        return self.current_time

    def end(self):
        return self.end_time
        
    def attach(self, start_time, time_delta, observer):
        timer_task = TimerTask(start_time, time_delta, observer)
        
        self.timer_lock.acquire()
        self.observer_list.append(timer_task)
        self.observer_list.sort(key = lambda task: task.next_moment())
        self.timer_lock.release()

        return timer_task

    def detach(self, timer_task):
        self.timer_lock.acquire()
        self.observer_list = [x for x in self.observer_list if x != timer_task]
        self.timer_lock.release()

    def setup(self):
        self.stop_event   = threading.Event()
        self.timer_lock   = threading.RLock()
        self.timer_thread = threading.Thread(target = self.__tick__)
        
    def start(self):
        self.timer_thread.start()

    def stop(self):
        self.stop_event.set()
        self.timer_thread.join()

    def free(self):
        pass
