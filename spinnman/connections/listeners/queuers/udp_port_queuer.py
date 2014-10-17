import socket
import logging
from spinnman.connections.listeners.queuers.abstract_port_queuer import \
    AbstractPortQueuer

logger = logging.getLogger(__name__)

class UDPPortQueuer(AbstractPortQueuer):
    '''
    thread that holds a _queue to try to stop the loss of packets from the socket
    '''

    def __init__(self, connection):
        AbstractPortQueuer.__init__(self, connection)

    def run(self):
        '''
        runs by just putting packets into a non-blocking _queue for the port listener to read from
        '''
        logger.info("[port_queuer] starting")
        while not self._done:
            try:
                data, addr = self._connection.receive_raw()
                self._queue.append(data)
            except socket.timeout:
                pass
        self._queue.append(None)
        self._exited = True














