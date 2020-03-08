import sys as sys
import time
import yaml
import importlib
import multiprocessing as mp
import logging as logging
import traceback as traceback
import signal as signal
import pandas as pd

class BackTester:
    def __init__(self, config):
        self.log_handler = logging.getLogger()
        self.test_config = config
        self.strategies  = []

        signal.signal(signal.SIGTERM, self.__signal__)
        signal.signal(signal.SIGINT, self.__signal__)

    def __signal__(self, signum, frame):
        self.stop()
    
    def start(self):
        strategy_folder = 'Strategy'
        for test_name in self.test_config:
            strategy_name   = self.test_config[test_name]['name']
            strategy_module = importlib.import_module(
                strategy_folder + '.' + strategy_name, None
            )

            if strategy_module is not None:
                strategy_init = getattr(strategy_module, strategy_name)
                self.strategies.append(strategy_init(
                    test_name, self.test_config[test_name])
                )

        process_list = []
        for strategy in self.strategies:
            process = mp.Process(target = strategy.start)
            process_list.append(process)
            process.start()

        try:
            while len(process_list) > 0:
                process_list = list(filter(lambda process: (process.is_alive()), process_list))
                time.sleep(1)
        except:
            self.log_handler.error(traceback.format_exception(*sys.exc_info()))
        finally:
            for process in process_list:
                process.join()

            score = {}
            for strategy in self.strategies:
                if strategy.error() is not None:
                    error, stack = strategy.error()
                    self.log_handler.error(error)
                    self.log_handler.error(stack)
                else:
                    name   = strategy.name()
                    metric = strategy.metric()
                    score[name] = metric
            
            score = pd.DataFrame.from_dict(score)
            score.to_csv('back_tester.csv', encoding = 'cp950')
                    
    def stop(self):
        for strategy in self.strategies:
            strategy.stop()
            
if __name__ == '__main__':
    back_tester = None
    try:
        with open('back_tester.yaml', 'r') as stream:
            print('Load config file')
            config  = yaml.load(stream)
            print('Create test object')
            back_tester = BackTester(config)
            print('Start test cases')
            back_tester.start()
            print('Test cases finish')
    except Exception as e:
        print(traceback.format_exception(*sys.exc_info()))
    finally:
        back_tester.stop()
