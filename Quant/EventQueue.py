import sys as sys
import threading as threading
import collections as collections
import traceback as traceback

class EventQueue:
    def __init__(self, log_handler):
        self.event_handler = collections.defaultdict(list)
        self.event_lock    = threading.RLock()
        self.log_handler   = log_handler

    def submit(self, event):
        self.log_handler.info('Submit ', event)

        try:
            self.event_lock.acquire()
            observer_list = self.event_handler.get(event.type)
            if observer_list is not None:
                for observer in observer_list:
                    observer(event)
        except:
            self.log_handler.error(traceback.format_exception(*sys.exc_info()))
        finally:
            self.event_lock.release()

    def attach(self, event_type, observer):
        self.event_lock.acquire()
        if observer not in self.event_handler[event_type]:
            self.event_handler[event_type].append(observer)
        self.event_lock.release()

    def detach(sef, event_type, observer):
        self.event_lock.acquire()
        observer_list = self.event_handler.get(event_type)
        if observer_list is None:
            self.event_lock.release()
            return
        else:
            if observer in observer_list:
                observer_list.remove(observer)
            if len(observer_list) <= 0:
                self.event_handler.pop(event_type)
        self.event_lock.release()
