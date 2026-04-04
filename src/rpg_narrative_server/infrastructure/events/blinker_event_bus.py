from collections import defaultdict

from blinker import Signal


class BlinkerEventBus:
    def __init__(self):
        self._signals = defaultdict(Signal)
        self._receivers = []

    def publish(self, event: object):
        signal = self._signals[type(event)]
        signal.send(self, event=event)

    def subscribe(self, event_type, handler):
        def wrapper(sender, **kwargs):
            handler(kwargs["event"])

        self._receivers.append(wrapper)
        self._signals[event_type].connect(wrapper, weak=False)
