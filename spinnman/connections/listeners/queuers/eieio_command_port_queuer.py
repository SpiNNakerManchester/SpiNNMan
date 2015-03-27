import logging
from spinnman.connections.listeners.queuers.abstract_port_queuer import \
    AbstractPortQueuer

logger = logging.getLogger(__name__)


class EIEIOCommandPortQueuer(AbstractPortQueuer):
    """ Queuer of EIEIO Commands
    """

    def __init__(self, connection):
        AbstractPortQueuer.__init__(self)
        self._connection = connection

    def _read_packet(self):
        return self._connection.receive_eieio_command_message()
