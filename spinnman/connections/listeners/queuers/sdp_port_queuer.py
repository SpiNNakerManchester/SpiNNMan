
import logging
from spinnman.connections.listeners.queuers.abstract_port_queuer import \
    AbstractPortQueuer

logger = logging.getLogger(__name__)


class SDPPortQueuer(AbstractPortQueuer):
    """ Queuer of SDP Messages
    """

    def __init__(self, connection):
        AbstractPortQueuer.__init__(self)
        self._connection = connection

    def _read_packet(self):
        return self._connection.receive_sdp_message()
