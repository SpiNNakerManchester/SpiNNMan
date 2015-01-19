from abc import ABCMeta
from abc import abstractmethod
from six import add_metaclass
from spinnman.data.little_endian_byte_array_byte_writer import \
    LittleEndianByteArrayByteWriter
from spinnman.exceptions import SpinnmanIOException
from spinnman.connections.abstract_classes.abstract_connection import \
    AbstractConnection


@add_metaclass(ABCMeta)
class AbstractUDPEIEIOCommandSender(AbstractConnection):
    """ A receiver of SCP messages
    """

    @abstractmethod
    def is_udp_eieio_command_sender(self):
        pass

    def send_eieio_command_message(self, eieio_command_message):
        """ Sends an SDP message down this connection

        :param eieio_command_message: The eieio message to be sent
        :type eieio_command_message: spinnman.messages.eieio.eieio_command_message.EIEIOCommandMessage
        :return: Nothing is returned
        :rtype: None
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    sending the message
        """
        if not self._can_send:
            raise SpinnmanIOException("Not connected to a remote host")

        # Create a writer for the message
        data_length = 0
        if eieio_command_message.data is not None:
            data_length = len(eieio_command_message.data)
        writer = LittleEndianByteArrayByteWriter()

        # Write the header
        eieio_command_message.eieio_command_header.write_command_header(writer)

        # Write any data
        if data_length != 0:
            writer.write_bytes(eieio_command_message.data)

        # Send the packet
        try:
            self._socket.send(writer.data)
        except Exception as e:
            raise SpinnmanIOException(str(e))
