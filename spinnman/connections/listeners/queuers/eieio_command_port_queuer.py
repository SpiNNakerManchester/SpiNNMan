import socket
import logging
from spinnman.connections.listeners.queuers.abstract_port_queuer import \
    AbstractPortQueuer

logger = logging.getLogger(__name__)


class EIEIOCommandPortQueuer(AbstractPortQueuer):
    '''
    thread that holds a _queue to try to stop the loss of packets from the socket
    '''

    def __init__(self, connection):
        AbstractPortQueuer.__init__(self, connection)

    def run(self):
        '''
        runs by just putting packets into a non-blocking _queue for the port listener to read from
        '''
        logger.debug("[eieio_command_port_queuer] starting")
        while not self._done:
            try:
                message = self._connection.receive_eieio_command_message()
                self._add_to_queue(message)
            except socket.timeout:
                pass
        self._add_to_queue(None)
        self._exited = True















