from abc import ABCMeta
from abc import abstractmethod
from six import add_metaclass

import struct

from spinnman.connections.abstract_classes.abstract_scp_sender import \
    AbstractSCPSender
from spinnman.connections.abstract_classes.udp_senders import udp_utils
from spinnman.exceptions import SpinnmanIOException


@add_metaclass(ABCMeta)
class AbstractUDPSCPSender(AbstractSCPSender):
    """ A sender of SCP messages
    """

    @abstractmethod
    def is_udp_scp_sender(self):
        pass

    def send_scp_request(self, scp_request):
        """ Sends an SCP request down this connection

         The following properties will be overwritten:

            * source_port will be set to 7
            * source_cpu will be set to 31
            * source_chip_x will be set to 0
            * source_chip_y will be set to 0

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
        udp_utils.update_sdp_header_for_udp_send(scp_request.sdp_header)

        # Send the packet
        try:
            self._socket.send(struct.pack("<2x") + scp_request.bytestring)
        except Exception as e:
            raise SpinnmanIOException(str(e))
