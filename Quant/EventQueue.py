from .Sequencer import *

class EventQueue:
    def __init__(self, log_handler):
        self.sequencer   = Sequencer(log_handler)
        self.log_handler = log_handler

    def submit(self, event):
        self.sequencer.submit(event)
        
    def attach(self, event_type, observer):
        self.sequencer.attach(event_type, observer)

    def detach(sefl, event_type, observer):
        self.sequencer.detach(event_type, observer)
