from abc import ABCMeta
from abc import abstractmethod
from six import add_metaclass
from spinnman.connections.abstract_classes.abstract_eieio_sender import \
    AbstractEIEIOSender
from spinnman.data.little_endian_byte_array_byte_writer import \
    LittleEndianByteArrayByteWriter
from spinnman.exceptions import \
    SpinnmanIOException, SpinnmanInvalidParameterTypeException
from spinnman.messages.eieio.abstract_messages.abstract_eieio_message import \
    AbstractEIEIOMessage


@add_metaclass(ABCMeta)
class AbstractUDPEIEIOSender(AbstractEIEIOSender):
    """ A receiver of SCP messages
    """

    @abstractmethod
    def is_udp_eieio_sender(self):
        pass

    def send_eieio_message(self, eieio_message):
        """ Sends an SDP message down this connection

        :param eieio_message: The eieio message to be sent
        :type eieio_message:\
                    :py:class:`spinnman.messages.eieio.abstract_messages.abstract_eieio_message.AbstractEIEIOMessage`
        :return: Nothing is returned
        :rtype: None
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    sending the message
        :raise spinnman.exceptions.SpinnmanInvalidParameterTypeException: If\
               the message passed to be sent does not inherit from
               :py:class:`spinnman.messages.eieio.abstract_messages.abstract_eieio_message.AbstractEIEIOMessage`
        """
        if not self._can_send:
            raise SpinnmanIOException("Not connected to a remote host")

        # check that the packet to send is of a class inheriting from
        # AbstractEIEIOMessage, and therefore has the ability to write
        # the message using the write_eieio_message function
        if not isinstance(eieio_message, AbstractEIEIOMessage):
            raise SpinnmanInvalidParameterTypeException(
                "eieio_message", eieio_message.__class__,
                "The message to be sent needs to be inheriting "
                "from AbstractEIEIOMessage")

        # create the byte writer
        writer = LittleEndianByteArrayByteWriter()

        # write the packet in the byte writer
        eieio_message.write_eieio_message(writer)

        # Send the packet
        try:
            self._socket.send(writer.data)
        except Exception as e:
            raise SpinnmanIOException(str(e))
