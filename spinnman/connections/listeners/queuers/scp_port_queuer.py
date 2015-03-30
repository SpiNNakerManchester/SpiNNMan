import logging
from spinnman.connections.listeners.queuers.abstract_port_queuer import \
    AbstractPortQueuer

logger = logging.getLogger(__name__)


class SCPPortQueuer(AbstractPortQueuer):
    """ Queuer of SCP Data
    """

    def __init__(self, connection):
        AbstractPortQueuer.__init__(self)
        self._connection = connection

    def _read_packet(self):
        return self._connection.read_scp_response()
