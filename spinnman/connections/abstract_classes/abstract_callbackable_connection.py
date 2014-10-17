from abc import ABCMeta
from abc import abstractmethod
from six import add_metaclass

@add_metaclass(ABCMeta)
class AbstractCallbackableConnection(object):

    def __init__(self):
        self._callback_listener = None
        self._callback_traffic_type = None

    @abstractmethod
    def register_callback(self, callback, traffic_type):
        pass

    @abstractmethod
    def deregister_callback(self, callback):
        pass