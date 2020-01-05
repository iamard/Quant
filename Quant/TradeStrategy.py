import multiprocessing as mp
import os as os
import sys as sys
import traceback as traceback
import signal as signal
import datetime as datetime
from .TimeManager import *
from .TradeMonitor import *
from .MarketState import *
from .TradeBroker import *

class TradeStrategy:
    def __init__(self, trade_name, trade_config, log_handler):
        self.out_folder  = os.path.join('Report', trade_name)
        if not os.path.exists(self.out_folder):
            os.makedirs(self.out_folder)
    
        self.stop_event  = mp.Event()    
        self.ticker_list = trade_config['ticker']

        start_time = trade_config['start']
        if isinstance(start_time, str) == True: \
            start_time = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M")

        end_time = trade_config['end']
        if isinstance(end_time, str) == True: \
            end_time = datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M")

        self.start_time    = start_time
        self.end_time      = end_time
        self.log_handler   = log_handler
        
        self.time_engine   = TimeManager(self.start_time,
                                         self.end_time,
                                         self.log_handler)

        self.trade_monitor = TradeMonitor(self.time_engine,
                                          self.log_handler)

        self.market_state  = MarketState(self.time_engine,
                                         self.log_handler)
        
        self.trade_broker  = TradeBroker(self.time_engine,
                                         trade_config['cash'],
                                         trade_config.get('signal', {}),
                                         trade_config['back'],
                                         self.log_handler)
                                        
    def begin(self, event):
        pass
                                        
    def term(self, event):
        pass
                                        
    def __trade__(self, event):
        if isinstance(event, StopEvent) == True:
            self.stop()
            self.term(event)

    def __market__(self, event):
        self.trade_broker.update() 

        if isinstance(event, OpenEvent) == True:
            self.open(event)
        elif isinstance(event, PauseEvent) == True:
            self.pause(event)
        elif isinstance(event, ResumeEvent) == True:
            self.resume(event)
        elif isinstance(event, CloseEvent) == True:
            self.close(event)
        else:
            raise TypeError("Unsupported market event type")

    def open(self, event):
        pass

    def pause(self, event):
        pass

    def resume(self, even):
        pass

    def close(self, event):
        pass

    def __quote__(self, event):
        self.quote(event)
    
    def quote(self, event):
        pass

    def buy(self, ticker, quantity, price):
        self.trade_broker.buy(ticker, quantity, price)
        
    def sell(self, ticker, quantity, price):
        self.trade_broker.sell(ticker, quantity, price)

    def start(self):
        try:
            signal.signal(signal.SIGTERM, signal.SIG_IGN)
            signal.signal(signal.SIGINT, signal.SIG_IGN)

            # Acquire resources
            self.time_engine.setup()
            self.trade_monitor.setup()
            self.market_state.setup()
            self.trade_broker.setup()

            self.trade_monitor.attach(TradeMonitor.TRADE_START, 
                                      self.__trade__)
            self.trade_monitor.attach(TradeMonitor.TRADE_STOP, 
                                      self.__trade__)

            self.market_state.attach(MarketState.MARKET_OPEN,
                                     self.__market__)
            self.market_state.attach(MarketState.MARKET_CLOSE, 
                                     self.__market__)

            self.trade_broker.attach(TradeBroker.BAR_DATA,
                                     self.ticker_list,
                                     self.__quote__)

            # Start each module
            self.trade_broker.start()
            self.market_state.start()
            self.trade_monitor.start()
            self.time_engine.start()

            # Wait all tasks done
            self.stop_event.wait()
        except:
            self.log_handler.error(traceback.format_exception(*sys.exc_info()))
        finally:
            # Stop each module
            self.time_engine.stop()
            self.trade_monitor.stop()
            self.market_state.stop()
            self.trade_broker.stop()

            # Release resources
            self.time_engine.free()
            self.trade_monitor.free()
            self.market_state.free()
            self.trade_broker.free()
        
    def stop(self):
        self.stop_event.set()
