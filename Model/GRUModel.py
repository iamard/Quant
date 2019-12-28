import numpy as np
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import GRU
from keras.layers import Dropout
from keras.optimizers import SGD
import matplotlib.pyplot as plt
from Scraper.DataQuoter import *
from Quant.TradeModel import *

# The core codes are from - I used the codes to test my framework
# https://ithelp.ithome.com.tw/articles/10206312
# Still need time to study RNN or CNN models for application

class GRUModel(TradeModel):
    def __init__(self, model_config, log_handler):
        # Initialize base class
        super().__init__()

        # Initialize this class
        self.ticker_id   = model_config['ticker'][0]
        self.start_date  = datetime.strptime(model_config['start'], '%Y-%m-%d %H:%M')
        self.end_date    = datetime.strptime(model_config['end'], '%Y-%m-%d %H:%M')
        self.x_train   = []
        self.y_train   = []
        self.scaler    = MinMaxScaler(feature_range = (0, 1))
        self.regressor = Sequential()

    def prepare(self):
        price_origin = DataQuoter(logging.getLogger()).price(
                   self.ticker_id,
                   self.start_date,
                   self.end_date
               )

        price_scaled = self.scaler.fit_transform(price_origin[self.ticker_id].ix[:, 0])
        
        x_train = []
        y_train = []
        for i in range(60, 1258):
            x_train.append(price_scaled[i - 60: i])
            y_train.append(price_scaled[i])
        x_train, y_train = np.array(x_train), np.array(y_train)
        self.x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))
        self.y_train = y_train

        x_test = []
        y_test = []
        for i in range(1258, 2000):
            x_test.append(price_scaled[i - 60: i])
            y_test.append(price_origin[self.ticker_id].ix[i, 0])
        x_test, y_test = np.array(x_test), np.array(y_test)

        self.x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1))
        self.y_test = y_test

    def train(self):
        # First GRU layer with Dropout regularisation
        self.regressor.add(GRU(units = 50, 
                               return_sequences = True, 
                               input_shape = (self.x_train.shape[1],1), 
                               activation = 'tanh'))
        self.regressor.add(Dropout(0.2))
        # Second GRU layer
        self.regressor.add(GRU(units = 50, 
                           return_sequences = True, 
                           input_shape = (self.x_train.shape[1], 1), 
                           activation = 'tanh'))
        self.regressor.add(Dropout(0.2))
        # Third GRU layer
        self.regressor.add(GRU(units = 50, 
                               return_sequences = True, 
                               input_shape = (self.x_train.shape[1], 1),
                               activation = 'tanh'))
        self.regressor.add(Dropout(0.2))
        # Fourth GRU layer
        self.regressor.add(GRU(units = 50, activation = 'tanh'))
        self.regressor.add(Dropout(0.2))
        # The output layer
        self.regressor.add(Dense(units = 1))
        # Compiling the RNN
        self.regressor.compile(optimizer = SGD(lr = 0.01, 
                                               decay = 1e-7, 
                                               momentum = 0.9, 
                                               nesterov = False),
                                               loss='mean_squared_error')
        # Fitting to the training set
        self.regressor.fit(self.x_train, self.y_train, epochs = 50, batch_size = 150)

    def predict(self):
        y_predict = self.regressor.predict(self.x_test)
        y_predict = self.scaler.inverse_transform(y_predict)

        plt.figure(figsize = (15, 10))
        plt.plot(self.y_test, color = 'green', label = 'Real Google Stock Price')
        plt.plot(y_predict, color = 'orange', label = 'Predicted Google Stock Price')
        plt.title('Google Stock Price Prediction')
        plt.xlabel('Time')
        plt.ylabel('Google Stock Price')
        plt.legend()
        plt.show()
