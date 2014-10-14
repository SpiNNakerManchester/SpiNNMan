from abc import ABCMeta
from abc import abstractmethod
from six import add_metaclass


@add_metaclass(ABCMeta)
class AbstractConnection(object):
    """ An abstract connection to the SpiNNaker board over some medium
    """

    @abstractmethod
    def is_connected(self):
        """ Determines if the medium is connected at this point in time

        :return: True if the medium is connected, False otherwise
        :rtype: bool
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    when determining the connectivity of the medium
        """
        pass

    @abstractmethod
    def close(self):
        """ Closes the connection

        :return: Nothing is returned
        :rtype: None
        :raise None: No known exceptions are raised
        """
        pass

    @classmethod
    def __subclasshook__(cls, othercls):
        """ Checks if all the abstract methods are present on the subclass
        """
        for C in cls.__mro__:
            for key in C.__dict__:
                item = C.__dict__[key]
                if hasattr(item, "__isabstractmethod__"):
                    if not any(key in B.__dict__ for B in othercls.__mro__):
                        return NotImplemented
        return True
