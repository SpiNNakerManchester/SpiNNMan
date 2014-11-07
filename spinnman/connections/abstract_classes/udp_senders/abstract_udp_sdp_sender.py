from abc import ABCMeta
from abc import abstractmethod
from six import add_metaclass

from spinnman.connections.abstract_classes.abstract_connection import AbstractConnection
from spinnman.data.little_endian_byte_array_byte_writer import \
    LittleEndianByteArrayByteWriter
from spinnman.exceptions import SpinnmanIOException
from spinnman.messages.udp_utils import udp_utils as utils


@add_metaclass(ABCMeta)
class AbstractUDPSDPSender(AbstractConnection):
    """ A sender of SDP messages
    """
    
    @abstractmethod
    def is_udp_sdp_sender(self):
        pass

    def send_sdp_message(self, sdp_message):
        """ Sends an SDP message down this connection
        
        :param sdp_message: The SDP message to be sent
        :type sdp_message: spinnman.messages.sdp.sdp_message.SDPMessage
        :return: Nothing is returned
        :rtype: None
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    sending the message
        """
        if not self._can_send:
            raise SpinnmanIOException("Not connected to a remote host")

        # Update the SDP headers for this connection
        utils.update_sdp_header(sdp_message.sdp_header, self._default_sdp_tag)

        # Create a writer for the mesage
        data_length = 0
        if sdp_message.data is not None:
            data_length = len(sdp_message.data)
        writer = LittleEndianByteArrayByteWriter()

        # Add the UDP padding
        writer.write_short(0)

        # Write the header
        sdp_message.sdp_header.write_sdp_header(writer)

        # Write any data
        if data_length != 0:
            writer.write_bytes(sdp_message.data)

        # Send the packet
        try:
            self._socket.send(writer.data)
        except Exception as e:
            raise SpinnmanIOException(str(e))

