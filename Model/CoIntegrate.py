import logging as logging
import datetime as datetime
import pandas as pandas
from statsmodels.tsa.stattools import coint
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from Scraper.DataQuoter import *
from Quant.TradeModel import *

# The core codes are from - I used the codes to test my framework
# https://github.com/Auquan/Tutorials/blob/master/Pairs%20Trading.ipynb
# Still need time to study underlying statistics algorithm

class CoIntegrate(TradeModel):
    def __init__(self, model_config, log_handler):
        # Initialize base class
        super().__init__()

        # Initialize this class
        self.data_quoter   = DataQuoter(log_handler)
        self.ticker_list   = model_config['ticker']
        self.start_date    = datetime.strptime(model_config['start'], '%Y-%m-%d %H:%M')
        self.end_date      = datetime.strptime(model_config['end'], '%Y-%m-%d %H:%M')
        self.price_frame   = None
        self.score_matrix  = None
        self.pvalue_matrix = None
        self.ticker_pair   = None
        self.log_handler   = log_handler

    def zscore(self, series):
        return (series - series.mean()) / np.std(series)

    def prepare(self):
        data = self.data_quoter.price(
                   self.ticker_list,
                   self.start_date,
                   self.end_date 
               )

        dict = {}
        for ticker in self.ticker_list:
            dict[ticker] = data[ticker]['adj_close']
            
        self.price_frame = pandas.DataFrame.from_dict(dict)
        self.price_frame.dropna()      
        
    def train(self):
        n = self.price_frame.shape[1]
        score_matrix = np.zeros((n, n))
        pvalue_matrix = np.ones((n, n))
        keys = self.price_frame.keys()
        pairs = []
        for i in range(n):
            for j in range(i + 1, n):
                S1 = self.price_frame[keys[i]]
                S2 = self.price_frame[keys[j]]
                result = coint(S1, S2)
                score = result[0]
                pvalue = result[1]
                score_matrix[i, j] = score
                pvalue_matrix[i, j] = pvalue
                if pvalue < 0.02:
                    pairs.append((keys[i], keys[j]))
        
        self.score_matrix = score_matrix
        self.pvalue_matrix = pvalue_matrix
        self.ticker_pair = pairs

    def predict(self):
        # Draw heat map
        # m = [0, 0.2, 0.4, 0.6, 0.8, 1]
        sns.heatmap(
            self.pvalue_matrix, xticklabels = self.ticker_list, yticklabels = self.ticker_list, 
                cmap = 'RdYlGn_r', mask = (self.pvalue_matrix >= 0.98)
        )
        plt.show()
