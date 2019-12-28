import multiprocessing as mp
import sys as sys
import traceback as traceback
import signal as signal

class TradeModel:
    def __init__(self):
        pass

    def prepare(self):
        pass

    def train(self):
        pass

    def predict(self):
        pass

    def start(self):
        try:
            signal.signal(signal.SIGTERM, signal.SIG_IGN)
            signal.signal(signal.SIGINT, signal.SIG_IGN)

            # Prepare train data
            self.prepare()

            # Train trade model
            self.train()

            # Predict test data
            self.predict()

        except:
            self.log_handler.error(traceback.format_exception(*sys.exc_info()))
            self.stop()
        finally:
            pass

    def stop(self):
        pass