import numpy as numpy
from Quant.TradeStrategy import *
from Plotter.LinePlot import *

class PairTradeMA(TradeStrategy):
    def __init__(self, strategy_name, trade_config, log_handler):
        # Initialize super class
        super().__init__(
            strategy_name,
            trade_config,
            log_handler
        )
 
        self.operation  = LinePlot('Trade', self.out_folder)
        self.equity_all = LinePlot('Equity', self.out_folder)

    def quote(self, event):    
        tickerA = self.ticker_list[0]
        tickerB = self.ticker_list[1]
        priceA  = event.data[tickerA]
        priceB  = event.data[tickerB]
        ratios  = priceA['adj_close'] / priceB['adj_close']
        mavg5   = ratios.rolling(window = 5, center = False).mean()
        mavg60  = ratios.rolling(window = 60, center = False).mean()
        std60   = ratios.rolling(window = 60, center = False).std()
        zscore  = (mavg5 - mavg60) / std60

        buy_price  = numpy.nan
        sell_price = numpy.nan
        if zscore[-1] > 2:
            print('@Sell')
            sell_price = priceA['close'][-1]
            self.sell(tickerA, 1, sell_price)
            buy_price  = priceB['close'][-1]
            self.buy(tickerB, 1, buy_price)
        elif zscore[-1] < -2:
            print('@Buy')
            buy_price  = priceA['close'][-1]
            self.buy(tickerA, 1, buy_price)
            sell_price = priceB['close'][-1]
            self.sell(tickerB, 1, sell_price)
        elif abs(zscore[-1]) < 0.5:
            pass

        self.operation.add({'time': event.event_time, 
                            tickerA: priceA['close'][-1],
                            tickerB: priceB['close'][-1],
                            'buy': buy_price,
                            'sell': sell_price})
        
        self.equity_all.add({"time": event.event_time,
                             "equity": self.trade_broker.equity()})

    def term(self, event):
        self.operation.plot(x_axis = 'time',
                            color = ['b', 'c', 'r', 'g'],
                            style = ['-', '-', 'None', 'None'],
                            marker = ['None', 'None', '^', '^'])

        self.equity_all.plot(x_axis = 'time',
                             color = ['b'],
                             style = ['-'],
                             marker = ['None'])
