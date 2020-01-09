import scipy.stats as st
from Quant.TradeStrategy import *
from Plotter.LinePlot import *

class PairTradePCT(TradeStrategy):
    def __init__(self, trade_name, trade_config):
        # Initialize super class
        super().__init__(
            trade_name,
            trade_config
        )

        self.z_signal_in  = st.norm.ppf(1 - 0.05 / 2)   # z-score threshold to open an order
        self.z_signal_out = st.norm.ppf(1 - 0.60 / 2)   # z-score threshold to close an order
        self.min_spread   = 0.035                       # Threshold for minimal allowed spread

        self.operation    = LinePlot()
        self.equity_all   = LinePlot()
        
    def quote(self, event):    
        tickerA = self.ticker_list[0]
        tickerB = self.ticker_list[1]
        priceA  = event.data[tickerA]
        priceB  = event.data[tickerB]
        returnA = priceA['close'].pct_change()
        returnB = priceB['close'].pct_change()
        spread  = returnA - returnB        
        zscore  = (spread[-1] - spread.mean()) / spread.std()
        
        print(zscore, self.z_signal_in, self.z_signal_out)
 
        quantityA = self.trade_broker.quantity(tickerA)
        quantityB = self.trade_broker.quantity(tickerB)
        if zscore >= -self.z_signal_out and \
           zscore <=  self.z_signal_out:
            self.log_handler.error('Close@')
            if quantityA > 0:
                self.sell(quantityA, priceA['close'][-1])
            if quantityB > 0:
                self.sell(quantityB, priceB['close'][-1])

        buy_price  = 0
        sell_price = 0
        if (abs(spread[-1]) >= self.min_spread):
            if zscore > self.z_signal_in: # and quantityA > 0:
                self.log_handler.error('Open A@')
                #self.sell(quantityA, price_A['close'][0]) 
                #self.buy(quantityB, price_B['close'][0])

                # Record buy and sell price
                sell_price = priceA['close'][-1]
                buy_price  = priceB['close'][-1]
            elif zscore < -self.z_signal_in: # and quantityB > 0:
                self.log_handler.error('Open B@')
                #self.buy(quantityA, price_A['close'][0])
                #self.sell(quantityB, price_B['close'][0])

                # Record buy and sell price
                buy_price  = priceA['close'][-1]
                sell_price = priceB['close'][-1]

        self.operation.add({'time': event.event_time, 
                            tickerA: priceA['close'][-1],
                            tickerB: priceB['close'][-1],
                            'buy': buy_price,
                            'sell': sell_price})
        
        self.equity_all.add({"time": event.event_time,
                             "equity": self.trade_broker.equity()})

    def term(self, event):
        self.operation.plot('operation.png',
                            color = ['b', 'c', 'r', 'g'],
                            style = ['-', '-', 'None', 'None'],
                            marker = ['None', 'None', '^', '^'])

        self.equity_all.plot('equity_all.png',
                             color = ['b'],
                             style = ['-'],
                             marker = ['None'])
