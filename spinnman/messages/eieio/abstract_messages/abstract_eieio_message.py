
from abc import ABCMeta
from abc import abstractmethod
from six import add_metaclass


@add_metaclass(ABCMeta)
class AbstractEIEIOMessage(object):
    """ Marker interface for an EIEIOMessage
    """

    @abstractmethod
    def write_eieio_message(self, byte_writer):
        """ Write the message to a byte writer

        :param byte_writer: The writer to write to
        :type byte_writer:\
                    :py:class:`spinnman.data.abstract_byte_writer.AbstractByteWriter`
        """
