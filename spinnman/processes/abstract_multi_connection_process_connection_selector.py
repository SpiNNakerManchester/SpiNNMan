from six import add_metaclass
from abc import ABCMeta
from abc import abstractmethod


@add_metaclass(ABCMeta)
class AbstractMultiConnectionProcessConnectionSelector(object):
    """ A connection selector for multi-connection processes
    """

    @abstractmethod
    def get_next_connection(self, connections):
        """ Get the index of the  next connection for the process from a list\
            of connections

        :param connections: a list of connections to choose from
        :rtype: int
        """
