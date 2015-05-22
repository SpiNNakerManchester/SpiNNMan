from spinnman.connections.abstract_classes.abstract_udp_connection import \
    AbstractUDPConnection
from spinnman import constants
from spinnman.connections.abstract_classes.udp_receivers.\
    abstract_udp_scp_receiver import AbstractUDPSCPReceiver
from spinnman.connections.abstract_classes.udp_receivers.\
    abstract_udp_sdp_receiver import AbstractUDPSDPReceiver
from spinnman.connections.abstract_classes.udp_senders.\
    abstract_udp_scp_sender import AbstractUDPSCPSender
from spinnman.connections.abstract_classes.udp_senders.\
    abstract_udp_sdp_sender import AbstractUDPSDPSender
from spinnman.messages.scp.abstract_messages.abstract_scp_request import \
    AbstractSCPRequest
from spinnman.messages.sdp.sdp_message import SDPMessage


class UDPSpinnakerConnection(AbstractUDPConnection, AbstractUDPSDPReceiver,
                             AbstractUDPSDPSender, AbstractUDPSCPSender,
                             AbstractUDPSCPReceiver):

    def __init__(self, local_host=None, local_port=None, remote_host=None,
                 default_sdp_tag=constants.DEFAULT_SDP_TAG, chip_x=0,
                 chip_y=0):
        AbstractUDPConnection.__init__(self, local_host, local_port,
                                       remote_host, constants.SCP_SCAMP_PORT)

        # Store the default sdp tag
        self._default_sdp_tag = default_sdp_tag
        self._chip_x = chip_x
        self._chip_y = chip_y

    def is_udp_scp_receiver(self):
        return True

    def is_udp_sdp_sender(self):
        return True

    def is_udp_sdp_reciever(self):
        return True

    def is_sdp_reciever(self):
        return True

    def is_scp_receiver(self):
        return True

    def is_udp_scp_sender(self):
        return True

    def connection_type(self):
        return constants.CONNECTION_TYPE.UDP_SPINNAKER

    def supports_sends_message(self, message):
        if (isinstance(message, SDPMessage) or
                isinstance(message, AbstractSCPRequest)):
            return True
        else:
            return False

    @property
    def chip_x(self):
        return self._chip_x

    @property
    def chip_y(self):
        return self._chip_y
