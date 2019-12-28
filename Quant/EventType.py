class EventBase:
    START_EVENT  = 1
    STOP_EVENT   = 2
    OPEN_EVENT   = 3
    PAUSE_EVENT  = 4
    RESUME_EVENT = 5
    CLOSE_EVENT  = 6
    BAR_EVENT    = 7

    def __init__(self, event_type, event_time, event_data = None):
        self.event_type = event_type
        self.event_time = event_time
        self.event_data = event_data

    def __str__(self):
        return str(self.event_time)
        
    @property
    def type(self):
        return self.event_type
        
    @property
    def time(self):
        return self.event_time

    @property
    def data(self):
        return self.event_data

class StartEvent(EventBase):
    def __init__(self, event_time):
        EventBase.__init__(self, EventBase.START_EVENT, event_time)
        
class StopEvent(EventBase):
    def __init__(self, event_time):
        EventBase.__init__(self, EventBase.STOP_EVENT, event_time)
        
class OpenEvent(EventBase):
    def __init__(self, event_time):
        EventBase.__init__(self, EventBase.OPEN_EVENT, event_time)

class PauseEvent(EventBase):
    def __init__(self, event_time):
        EventBase.__init__(self, EventBase.PAUSE_EVENT, event_time)

class ResumeEvent(EventBase):
    def __init__(self, event_time):
        EventBase.__init__(self, EventBase.RESUME_EVENT, event_time)
        
class CloseEvent(EventBase):
    def __init__(self, event_time):
        EventBase.__init__(self, EventBase.CLOSE_EVENT, event_time)

class BarEvent(EventBase):
    def __init__(self, event_time, price_value):
        EventBase.__init__(self, EventBase.BAR_EVENT, event_time, price_value)
