from six import add_metaclass
from abc import ABCMeta
from abc import abstractmethod


@add_metaclass(ABCMeta)
class AbstractMultiConnectionProcessConnectionSelector(object):
    """ A connection selector for multi-connection processes
    """

    @abstractmethod
    def __init__(self, connections):
        """
        :param connections: The connections to be used
        """

    @abstractmethod
    def get_next_connection(self, message):
        """ Get the index of the  next connection for the process from a list\
            of connections

        :param message: The SCP message to be sent
        :rtype: int
        """
