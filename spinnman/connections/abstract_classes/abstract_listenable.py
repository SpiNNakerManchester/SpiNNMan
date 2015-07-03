from six import add_metaclass
from abc import ABCMeta
from abc import abstractmethod


@add_metaclass(ABCMeta)
class AbstractListenable(object):

    @abstractmethod
    def get_receive_method(self):
        """ Get the method that receives for this connection
        """
