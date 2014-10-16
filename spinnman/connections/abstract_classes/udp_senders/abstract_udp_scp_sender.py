from abc import ABCMeta
from abc import abstractmethod
from six import add_metaclass

from spinnman.connections.abstract_classes.abstract_scp_sender import \
    AbstractSCPSender
from spinnman.data.little_endian_byte_array_byte_writer import \
    LittleEndianByteArrayByteWriter
from spinnman.exceptions import SpinnmanIOException
from spinnman import constants
from spinnman.messages.udp_utils import udp_utils as utils

@add_metaclass(ABCMeta)
class AbstractUDPSCPSender(AbstractSCPSender):
    """ A sender of SCP messages
    """

    @abstractmethod
    def is_udp_scp_sender(self):
        pass

    def send_scp_request(self, scp_request):
        """ Sends an SCP request down this connection

         Messages must have the following properties:

            * source_port is None or 7
            * source_cpu is None or 31
            * source_chip_x is None or 0
            * source_chip_y is None or 0

        tag in the message is optional - if not set the default set in the\
        constructor will be used.
        sequence in the message is optional - if not set (sequence number\
        last assigned + 1) % 65536 will be used
        
        :param scp_request: message packet to send
        :type scp_request:
                    :py:class:`spinnman.messages.scp.abstract_scp_request.AbstractSCPRequest`
        :return: Nothing is returned
        :rtype: None
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    sending the message
        """
        if not self._can_send:
            raise SpinnmanIOException("Not connected to a remote host")

        # Update the SDP headers for this connection
        utils.update_sdp_header(scp_request.sdp_header,
                                constants.DEFAULT_SDP_TAG)

        # Update the sequence for this connection
        if scp_request.scp_request_header.sequence is None:
            scp_request.scp_request_header.sequence = self._scp_sequence
            self._scp_sequence = (self._scp_sequence + 1) % 65536

        # Create a writer for the mesage
        writer = LittleEndianByteArrayByteWriter()

        # Add the UDP padding
        writer.write_short(0)

        # Write the SCP message
        scp_request.write_scp_request(writer)

        # Send the packet
        try:
            self._socket.send(writer.data)
        except Exception as e:
            raise SpinnmanIOException(str(e))
