from blinker import Signal
from collections import defaultdict


class BlinkerEventBus:
    def __init__(self):
        self._signals = defaultdict(Signal)

    def publish(self, event: object):
        signal = self._signals[type(event)]
        signal.send(event)

    def subscribe(self, event_type, handler):
        def wrapper(event):
            handler(event)

        self._signals[event_type].connect(wrapper)
