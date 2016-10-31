import threading
import Queue as queue
import sys

class Observerable:
    def __init__(self):
        self.__observers   = []
        self.__event_queue = queue.Queue()

    def __wrap_func(self, observer, args):
        try:
            observer(*args)
        except:
            self.__event_queue.put(sys.exc_info())
        self.__event_queue.put(None)

    def add_observer(self, observer):
        self.__observers.append(observer)

    def del_observer(self, observer):
        self.__observers.remove(observer)

    def run_observer(self, args):
        threads = []

        for observer in self.__observers:
            threads.append(threading.Thread(target = self.__wrap_func, args = [observer, args]))

        for thread in threads:
            thread.start()

    def wait_observer(self):
        count = 0
        while True:
            info = self.__event_queue.get()
            if info == None:
                count += 1
                if count == len(self.__observers):
                    break
            else:
                raise info[1]
