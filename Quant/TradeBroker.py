import os as os
import threading as threading
import datetime as datetime
import numpy as np
import pandas as pandas
import plotly.graph_objs as go
from plotly.offline import plot
from .DataFeed import *
from .EventQueue import *
from .EventType import *
from .Portfolio import *

class DataSource:
    def __init__(self, time_beat, signal_dict, look_back, log_handler):
        # Initialize parent class
        super().__init__()

        self.time_beat   = time_beat
        self.price_data  = {}
        self.data_feed   = DataFeedFactory.create(
            signal_dict,
            log_handler)
        self.trade_date  = None
        self.look_back   = look_back
        self.log_handler = log_handler

    def is_tick(self):
        return False

    def __query__(self, ticker_id):
        price_data  = self.quote([ticker_id])[ticker_id]
        curr_time   = self.time_beat.time()
        curr_date   = curr_time.date()
        index_value = price_data.index.get_loc(curr_date, method = 'nearest')
        if price_data.index[index_value].date() > curr_time.date():
            self.log_handler.error('time inversion')

        return price_data.iloc[index_value]

    def trade(self, date):
        if date in self.trade_date:
            return True
        else:
            return False;
        
    def quote(self, ticker_list):
        quote_list = []
        for ticker_id in ticker_list:
            price_data = self.price_data.get(ticker_id, None)
            if price_data is None:
                quote_list.append(ticker_id)

        if len(quote_list) > 0:
            price_data = self.data_feed.quote(
                quote_list,
                self.time_beat.base() - datetime.timedelta(days = self.look_back + 30),
                self.time_beat.end()
            )
            self.price_data.update(price_data)
            for ticker_id in quote_list:
                if self.trade_date is None:
                    self.trade_date = self.price_data[ticker_id].index.date
                else:
                    self.trade_date = self.trade.intersection(
                        self.price_data[ticker_id].index.date
                    )  
           
        price_data = {}
        for ticker_id in ticker_list:
            price_data[ticker_id] = self.price_data.get(ticker_id, None)
            if price_data is None:
                return None

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

    def dividend(self, ticker_id):
        price_data  = self.__query__(ticker_id)
        return price_data['dividend']

class Order:
        ORDER_STATUS_SUBMITTED = 'Submitted'
        ORDER_STATUS_COMMITTED = 'Committed'

        ORDER_ACTION_BUY = 'buy'
        ORDER_ACTION_SELL = 'sell'

        def __init__(self, order_time, action_type, ticker_id, quantity, trade_price, commission):
            self.trade_status = Order.ORDER_STATUS_SUBMITTED
            self.order_time   = order_time
            self.action_type  = action_type
            self.ticker_id    = ticker_id
            self.quantity     = quantity
            self.trade_price  = trade_price
            self.commission   = commission

        def update(self, status):
            self.trade_status = status
            
        def status(self):
            return self.trade_status

        def time(self):
            return self.order_time
            
        def action(self):
            return self.action_type

        def ticker(self):
            return self.ticker_id
            
        def price(self):
            return self.trade_price

        def quantity(self):
            return self.quantity
            
class TradeBroker:
    BAR_DATA = EventBase.BAR_EVENT
        
    def __init__(self, time_beat, data_quoter, start_cash, look_back, out_folder, log_handler):    
        self.time_beat    = time_beat
        self.data_quoter  = data_quoter
        self.order_list   = []
        self.portfolio    = Portfolio(data_quoter,
                                      start_cash, 
                                      log_handler)
        self.look_back    = look_back
        self.last_update  = None
        self.event_queue  = None
        self.timer_lock   = None
        self.quote_timer  = None
        self.trade_record = pandas.DataFrame()
        self.trade_action = pandas.DataFrame()
        self.out_folder   = out_folder
        self.attach_list  = []
        self.log_handler  = log_handler

    def buy(self, ticker_id, quantity, trade_price):
        commission = (quantity * trade_price) * 0.001
        required   = (quantity * trade_price) + commission
        if self.portfolio.cash() < required:
            return None
    
        order = Order(self.time_beat.time(),
                      Order.ORDER_ACTION_BUY,
                      ticker_id,
                      quantity,
                      trade_price,
                      commission)
        self.order_list.append(order)
        return order
    
    def sell(self, ticker_id, quantity, trade_price):
        if self.portfolio.quantity(ticker_id) < quantity:
            return None

        order = Order(self.time_beat.time(),
                      Order.ORDER_ACTION_SELL,
                      ticker_id,
                      quantity,
                      trade_price,
                      (quantity * trade_price) * 0.001)
        self.order_list.append(order)
        return order

    def quantity(self, ticker_id):
        return self.portfolio.quantity(ticker_id)

    def update(self):
        curr_time = self.time_beat.time()
        if self.last_update == None or \
           self.last_update != curr_time:
           
            for order in self.order_list:
                if order.action_type == Order.ORDER_ACTION_BUY:
                    if order.trade_price >= self.data_quoter.low(order.ticker_id):
                        self.portfolio.transact(Portfolio.ACTION_BUY,
                                                order.ticker_id,
                                                order.quantity,
                                                order.trade_price,
                                                order.commission)
                        order.update(Order.ORDER_STATUS_COMMITTED)
                elif order.action_type == Order.ORDER_ACTION_SELL:
                    if order.trade_price <= self.data_quoter.high(order.ticker_id):
                        self.portfolio.transact(Portfolio.ACTION_SELL,
                                                order.ticker_id,
                                                order.quantity,
                                                order.trade_price,
                                                order.commission)
                        order.update(Order.ORDER_STATUS_COMMITTED)

                if order.status() == Order.ORDER_STATUS_COMMITTED:
                    self.trade_record = self.trade_record.append(
                        { 'time': order.order_time,
                          'ticker_id': order.ticker_id,
                          'action': order.action_type,
                          'price': order.trade_price,
                          'quantity': order.quantity,
                          'commission': order.commission
                        },
                        ignore_index = True
                    )
                
                    action = order.ticker_id + '_' + order.action_type
                    self.trade_action = self.trade_action.append(
                        { 'date': order.order_time.date(),
                          action: order.trade_price},
                        ignore_index = True
                    )
                    
            self.order_list.clear()
            self.portfolio.update()
            self.last_update = curr_time

    def cash(self):
        return self.portfolio.cash()

    def equity(self):
        self.update()
        return self.portfolio.equity()

    def __time__(self, time):
        start_date = (time - datetime.timedelta(days = self.look_back + 30)).date()
        end_date   = time.date()
    
        if self.data_quoter.trade(end_date) == False:
            self.log_handler.info('Not a trading date', end_date)
            return
        
        ticker_data = self.data_quoter.quote(self.attach_list)
        if ticker_data is None:
            self.log_handler.debug('No available price data!')
            return

        self.log_handler.info('Trade on ' + end_date.strftime('%Y-%m-%d'))

        event_data = {}
        for ticker_id in self.attach_list:
            # Add dividend value to cash
            dividend    = self.data_quoter.dividend(ticker_id) * \
                          self.portfolio.quantity(ticker_id)
            if dividend != 0:
                self.log_handler.error(
                    'Get {} dividend {} on {}'.format(ticker_id, dividend, time)
                )
                self.portfolio.dividend(ticker_id, dividend)

            price_data  = ticker_data[ticker_id]
            end_index   = price_data.index.get_loc(end_date)
            start_index = end_index - self.look_back    
            if start_index < 0:
                self.log_handler.debug('Not have enough data')
                return

            price_data = price_data.iloc[start_index: end_index]
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

        # Restore ticker list in portfolio
        self.attach_list = self.portfolio.ticker()

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
        
    def report(self):
        price_dict  = self.data_quoter.quote(self.attach_list)
        price_list  = []
        for ticker_id in self.attach_list:
            frame = price_dict[ticker_id][['close']]
            frame.columns = [ticker_id]
            price_list.append(frame)
        price_frame = pandas.concat(price_list, axis = 1)
        price_frame.reset_index(inplace = True)
        price_frame.date = price_frame.date.apply(lambda x: x.date())

        if self.trade_action.empty == False:
            price_frame = pandas.merge(
                price_frame, 
                self.trade_action,
                on = 'date',
                how = 'outer')

            price_frame.sort_values(by = 'date')
            price_frame.to_csv(
                os.path.join(self.out_folder, 'Trade.csv'),
                encoding = 'cp950',
                index = False
            )

        price_frame.set_index('date', inplace = True)
            
        # Plotly setup and traces
        figure = go.Figure()

        for ticker_id in self.attach_list:
            figure.add_trace(go.Scatter(x = price_frame.index, 
                                        y = price_frame[ticker_id].values,
                                        name = ticker_id,
                                        mode = 'lines'))
            buy = ticker_id + '_buy'
            if buy in price_frame.columns:
                figure.add_trace(go.Scatter(x = price_frame.index, 
                                            y = price_frame[buy].values,
                                            name = buy,
                                            mode = 'markers'))
                            
            sell = ticker_id + '_sell'
            if sell in price_frame.columns:
                figure.add_trace(go.Scatter(x = price_frame.index, 
                                            y = price_frame[sell].values,
                                            name = sell,
                                            mode = 'markers'))
                                            
        figure.update_layout(
            {'width': 800,
             'height': 600,
             'xaxis': {'showgrid': False, 'tickangle': 60 },
             'yaxis': {'gridcolor': 'black'},
             'paper_bgcolor': 'rgb(255, 255, 255)',
             'plot_bgcolor': 'rgb(255, 255, 255)',
            }
        )
        #figure.show()
        figure.write_image(os.path.join(self.out_folder, 'Trade.png')) 

        if self.trade_record.empty:
            return

        # Sort according time
        self.trade_record.sort_values(by = 'time')

        # Reserve column order
        data = self.trade_record[['time', 'ticker_id', 'action', 'price', 'quantity', 'commission']]

        # Save to csv file
        data.to_csv(
            os.path.join(self.out_folder, 'Record.csv'),
            encoding = 'cp950',
            index = False
        )
