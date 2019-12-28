from flask import Flask
from flask_ini import FlaskIni
import click
from BackTester import *
#from ModelTrain import *

#TBD
app = Flask(__name__)

#@app.cli.command()
#def TrainModel():
#    trainer = None
#    try:
#        trainer = ModelTrain()
#        trainer.start()
#    except Exception as e:
#        print(traceback.format_exception(*sys.exc_info()))
#        trainer.stop()

@app.cli.command()
def test():
    back_tester = None
    try:
        back_tester = BackTester(TradeAgent())
        back_tester.start()
    except Exception as e:
        print(traceback.format_exception(*sys.exc_info()))
        back_tester.stop()

