import sys as sys
import time
import yaml
import importlib
import multiprocessing as mp
import logging as logging
import traceback as traceback
import signal as signal

class ModelTrain:
    def __init__(self, config):
        self.log_handler  = logging.getLogger()
        self.train_config = config
        self.train_models = []

        signal.signal(signal.SIGTERM, self.__signal__)
        signal.signal(signal.SIGINT, self.__signal__)

    def __signal__(self, signum, frame):
        self.stop()

    def start(self):
        model_folder = 'Model'
        for model in self.train_config:
            model_name   = self.train_config[model]['name']
            model_module = importlib.import_module(
                model_folder + '.' + model_name, None
            )

            if model_module is not None:
                model_init = getattr(model_module, model_name)
                self.train_models.append(model_init(
                    self.train_config[model], self.log_handler)
                )
                
        process_list = []
        for train_model in self.train_models:
            process = mp.Process(target = train_model.start)
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
            
    def stop(self):
        for model in self.train_models:
            model.stop()

if __name__ == '__main__':
    trainer = None
    try:
        with open('model_train.yaml', 'r') as stream:
            config  = yaml.load(stream)
            trainer = ModelTrain(config)
            trainer.start()
    except Exception as e:
        print(traceback.format_exception(*sys.exc_info()))
        trainer.stop()