import pandas as pd
import numpy as np
from .DataFeed import *
from Plotter.LinePlot import *

class SharpeRatio:
    def __init__(self, period = 252):
        self.period = period

    def metric(self, trade_return, trade_metric):
        return_series = trade_return['return'] 
        mean_value    = np.mean(return_series)
        std_value     = np.std(return_series)
        if std_value  == 0.0:
            std_value = 1
        trade_metric['sharpe'] = np.sqrt(self.period) * mean_value / std_value

class MaxDrawDown:
    def __init__(self):
        pass

    def metric(self, trade_return, trade_metric):
        return_series = trade_return['return'].cumsum()
    
        # End of the period
        end_index   = np.argmax(
            np.maximum.accumulate(return_series.values) - return_series.values
        )
        
        # Start of the period
        if end_index == 0:
            start_index = 0
        else:
            start_index = np.argmax(return_series.values[: end_index])
 
        # Record MDD metrics
        trade_metric['MDD ratio']  = abs(
            100.0 * (return_series[end_index] - return_series[start_index])
        )
        trade_metric['MDD start']  = trade_return['date'].iloc[start_index].strftime('%Y-%m-%d')
        trade_metric['MDD end']    = trade_return['date'].iloc[end_index].strftime('%Y-%m-%d')
        trade_metric['MDD period'] = end_index - start_index

class TradeMetric:
    def __init__(self, benchmark, period, out_folder, log_handler):
        if isinstance(benchmark, list) == True:
            self.benchmark = benchmark
        else:
            self.benchmark = [ benchmark ]
        self.data_feed     = DataFeedFactory.create({}, log_handler)
        self.metric_period = period
        self.equity_figure = LinePlot('Equity', out_folder)
        self.return_figure = LinePlot('Return', out_folder)
        self.metric_list   = [ SharpeRatio(), MaxDrawDown() ]
        self.trade_metric  = {}
        self.log_handler   = log_handler

    def record(self, time, equity):
        self.equity_figure.add({'date': time, 'equity': equity})
        
    def metric(self):
        self.equity_figure.plot('Equity',
                               x_axis = 'date',
                               color = ['b'],
                               style = ['-'],
                               marker = ['None'])
    
        # Calculate metric value
        trade_return = self.equity_figure.data()
        trade_return.reset_index(inplace = True)
        trade_return.sort_values(by = 'date')

        # Record start and end date
        start_date = trade_return['date'].iloc[0].strftime('%Y-%m-%d')
        end_date   = trade_return['date'].iloc[-1].strftime('%Y-%m-%d')

        # Create return frame
        trade_return['return'] = trade_return['equity'].pct_change().fillna(0.0)
        trade_return['date'] = trade_return['date'].apply(lambda x: x.date())
        trade_return = trade_return.drop('equity', 1)

        # Calculate metric
        for metric_obj in self.metric_list:
            metric_obj.metric(trade_return[['date', 'return']], self.trade_metric)
        
        # Calculate cum return
        trade_return['return'] = trade_return['return'].cumsum()
        
        # Fetch benchmark prices
        price_dict = self.data_feed.quote(self.benchmark, start_date, end_date)

        # Calculate benchmark return
        price_list = []
        for ticker in self.benchmark:
            price_list.append(
                price_dict[ticker][['adj_close']].rename(columns = { 'adj_close': ticker })
            )
        price_frame = pd.concat(price_list, axis = 0)
        for ticker in self.benchmark:
            price_frame[ticker] = price_frame[ticker].pct_change().fillna(0.0).cumsum()
        price_frame.reset_index(inplace = True)
        price_frame['date'] = price_frame['date'].apply(lambda x: x.date())

        trade_return = pd.merge(trade_return, price_frame, on = 'date')

        # Plot return figure
        sharpe    = 'Sharpe: {}'.format(round(self.trade_metric['sharpe'], 3))
        draw_down = 'MDD ratio/start/end/period: {}%/{}/{}/{}'.format(
            round(self.trade_metric['MDD ratio'], 3),
            self.trade_metric['MDD start'],
            self.trade_metric['MDD end'],
            self.trade_metric['MDD period'],
        )
        title = '\n'.join([sharpe, draw_down])

        self.return_figure.set(trade_return)

        self.return_figure.plot(title,
                                x_axis = 'date',
                                color = ['b', 'g'],
                                style = ['-', '-'],
                                marker = ['None', 'None'])
        return self.trade_metric
