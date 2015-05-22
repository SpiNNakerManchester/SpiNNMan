from six import add_metaclass
from abc import ABCMeta
from abc import abstractmethod


@add_metaclass(ABCMeta)
class AbstractEIEIODataElement(object):
    """ A marker interface for possible data elements in the EIEIO data packet
    """

    @abstractmethod
    def write_element(self, eieio_type, byte_writer):
        """ Write the element to the writer given the type

        :param eieio_type: The type of the message being written
        :type eieio_type:\
                    :py:class:`spinnman.messages.eieio.eieio_type.EIEIOType`
        :param byte_writer: The writer to write to
        :type byte_writer:\
                    :py:class:`spinnman.data.abstract_byte_writer.AbstractByteWriter`
        :raise SpinnmanInvalidParameterException: If the type is incompatible\
                    with the element
        """
