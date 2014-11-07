from abc import ABCMeta
from abc import abstractmethod
from six import add_metaclass

from spinnman.connections.abstract_classes.abstract_connection \
    import AbstractConnection


@add_metaclass(ABCMeta)
class AbstractEIEIOReceiver(AbstractConnection):

    @abstractmethod
    def is_eieio_receiver(self):
        pass

    @abstractmethod
    def receive_eieio_message(self, timeout=None):
        pass