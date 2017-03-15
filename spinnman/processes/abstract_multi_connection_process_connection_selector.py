from six import add_metaclass

from spinn_utilities.abstract_base import AbstractBase, abstractmethod


@add_metaclass(AbstractBase)
class AbstractMultiConnectionProcessConnectionSelector(object):
    """ A connection selector for multi-connection processes
    """

    # connections will be used when worked out how

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
