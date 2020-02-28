import multiprocessing as mp
import os as os
import sys as sys
import logging as logging
import traceback as traceback
import signal as signal
import datetime as datetime
from .TradeMetric import *
from .TimeManager import *
from .TradeMonitor import *
from .MarketState import *
from .TradeBroker import *

class TradeStrategy:
    def __init__(self, trade_name, trade_config):
        self.out_folder  = os.path.join('Report', trade_name)
        if not os.path.exists(self.out_folder):
            os.makedirs(self.out_folder)

        self.trade_name  = trade_name
            
        # Setup log and file handlers
        logging.basicConfig(level = logging.NOTSET)
        self.log_handler = logging.getLogger(trade_name)
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

        self.time_engine   = TimeManager(self.start_time,
                                         self.end_time,
                                         self.log_handler)

        self.data_source   = DataSource(self.time_engine,
                                        trade_config.get('signal', {}),
                                        trade_config['back'],
                                        self.log_handler)

        self.trade_monitor = TradeMonitor(self.time_engine,
                                          self.log_handler)

        self.market_state  = MarketState(self.time_engine,
                                         self.data_source,
                                         self.log_handler)
        
        self.trade_broker  = TradeBroker(self.time_engine,
                                         self.data_source,
                                         trade_config['cash'],
                                         trade_config['back'],
                                         self.log_handler)
        
        self.trade_metric  = TradeMetric('0050.tw',
                                         252,
                                         self.out_folder,
                                         self.log_handler)
                                        
    def begin(self, event):
        pass
                                        
    def term(self, event):
        pass
                                        
    def __trade__(self, event):
        if isinstance(event, StopEvent) == True:
            print(event.time)
            self.trade_metric.metric()

        if isinstance(event, StartEvent) == True:
            self.begin(event)
        elif isinstance(event, StopEvent) == True:
            self.term(event)
            self.stop()
        else:
            raise TypeError("Unsupported trade event type")

    def __market__(self, event):
        if isinstance(event, CloseEvent) == True:
            self.trade_metric.record(
                event.time, self.trade_broker.equity()
            )

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

            output_file   = os.path.join(self.out_folder, self.trade_name + '.log')
            file_handler  = logging.FileHandler(output_file)
            file_handler.setLevel(logging.INFO)
            log_formatter = logging.Formatter(
                           fmt = '%(asctime)s %(levelname)s: %(message)s',
                           datefmt = '%Y-%m-%d %H:%M:%S'
                        )
            file_handler.setFormatter(log_formatter)
            self.log_handler.addHandler(file_handler)
            
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
        
            self.log_handler.handlers.clear()
        
    def stop(self):
        self.stop_event.set()
