import logging
from spinnman.connections.listeners.queuers.abstract_port_queuer import \
    AbstractPortQueuer

logger = logging.getLogger(__name__)


class UDPPortQueuer(AbstractPortQueuer):
    """ Queuer of Raw UDP messages
    """

    def __init__(self, connection):
        AbstractPortQueuer.__init__(self)
        self._connection = connection

    def _read_packet(self):
        data, _ = self._connection.receive_raw()
        return data
