"""
UDPBMPConnection
"""

# spinnman imports
from spinnman import constants
from spinnman.connections.abstract_classes.abstract_udp_connection import \
    AbstractUDPConnection
from spinnman.connections.abstract_classes.udp_receivers.\
    abstract_udp_scp_bmp_receiver import \
    AbstractUDPSCPBMPReceiver
from spinnman.connections.abstract_classes.udp_receivers.\
    abstract_udp_sdp_receiver import AbstractUDPSDPReceiver
from spinnman.connections.abstract_classes.udp_senders.\
    abstract_udp_scp_bmp_sender import \
    AbstractUDPSCPBMPSender
from spinnman.connections.abstract_classes.udp_senders.\
    abstract_udp_sdp_sender import AbstractUDPSDPSender
from spinnman.messages.scp.abstract_messages.abstract_scp_bmp_request import \
    AbstractSCPBMPRequest
from spinnman.messages.sdp.sdp_message import SDPMessage


class UDPBMPConnection(
        AbstractUDPConnection, AbstractUDPSDPReceiver, AbstractUDPSDPSender,
        AbstractUDPSCPBMPSender, AbstractUDPSCPBMPReceiver):
    """ A BMP connection which supports queries to the BMP of a SpiNNaker\
        machine
    """

    def __init__(self, cabinet, frame, boards, local_host=None,
                 local_port=None, remote_host=None):
        AbstractUDPConnection.__init__(
            self, local_host, local_port, remote_host,
            constants.SCP_SCAMP_PORT)
        self._cabinet = cabinet
        self._frame = frame
        self._boards = boards

    @property
    def cabinet(self):
        """ The cabinet id of the BMP

        :rtype: int
        """
        return self._cabinet

    @property
    def frame(self):
        """ The frame id of the BMP

        :rtype: int
        """
        return self._frame

    @property
    def boards(self):
        """ The set of boards supported by the BMP

        :rtype: iterable of int
        """
        return self._boards

    def supports_sends_message(self, message):
        """
        helper method for spinnman to deduce if this connection is valid for
        this message type
        :param message: message to check if valid to send
        :return: true if valid, false otherwise
        """
        if isinstance(message, AbstractSCPBMPRequest):
            return True
        if isinstance(message, SDPMessage):
            return True
        else:
            return False

    def connection_type(self):
        """
        returns the type of the connection type
        :return:
        """
        return constants.CONNECTION_TYPE.UDP_BMP

    def is_sdp_reciever(self):
        """
        helper method for isinstance
        :return:
        """
        return True

    def is_udp_sdp_reciever(self):
        """
        helper method for isinstance
        :return:
        """
        return True

    def is_scp_receiver(self):
        """
        helper method for isinstance
        :return:
        """
        return True

    def is_udp_sdp_sender(self):
        """
        helper method for isinstance
        :return:
        """
        return True

    def is_udp_scp_sender(self):
        """
        helper method for isinstance
        :return:
        """
        return True

    def is_udp_scp_bmp_sender(self):
        """
        helper method for isinstance
        :return:
        """
        return True

    def is_udp_scp_bmp_receiver(self):
        """
        helper method for isinstance
        :return:
        """
        return True
