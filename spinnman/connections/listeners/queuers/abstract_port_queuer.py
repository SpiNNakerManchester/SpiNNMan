import threading
import collections
import socket
import logging
from abc import ABCMeta
from abc import abstractmethod
from six import add_metaclass

logger = logging.getLogger(__name__)

@add_metaclass(ABCMeta)
class AbstractPortQueuer(threading.Thread):

    def __init__(self, connection):
        threading.Thread.__init__(self)
        self._queue = collections.deque()
        self._done = False
        self._exited = False
        self._connection = connection
        self.setDaemon(True)

    def stop(self):
        '''
        method to kill the thread
        '''
        logger.info("[_queuer] Stopping")
        self._done = True
        while not self._exited:
            pass

    @abstractmethod
    def run(self):
        pass

    def get_packet(self):
        '''
        allows the port listener to pull a packet from the non-blocking _queue
        '''
        got = False
        packet = None
        while not got:
            if len(self._queue) != 0:
                packet = self._queue.popleft()
                got = True
        return packet
