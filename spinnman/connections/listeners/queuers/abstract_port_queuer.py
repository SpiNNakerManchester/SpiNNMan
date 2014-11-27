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
        self._queue_condition = threading.Condition()
        self._done = False
        self._exited = False
        self._connection = connection
        self.setDaemon(True)

    def stop(self):
        """
        method to kill the thread
        """
        logger.debug("[_queuer] Stopping")
        self._queue_condition.acquire()
        self._done = True
        self._queue_condition.notify()
        self._queue_condition.release()

        self._queue_condition.acquire()
        while not self._exited:
            self._queue_condition.wait()
        self._queue_condition.release()

    @abstractmethod
    def run(self):
        pass

    def get_packet(self):
        '''
        allows the port listener to pull a packet from the non-blocking _queue
        '''
        got = False
        while not got:
            self._queue_condition.acquire()
            while len(self._queue) == 0 and not self._done:
                self._queue_condition.wait()
            packet = None
            if not self._done:
                packet = self._queue.popleft()
            self._queue_condition.release()
            if packet is not None:
                return packet

    def _add_to_queue(self, packet):
        self._queue_condition.acquire()
        self._queue.append(packet)
        self._queue_condition.notify()
        self._queue_condition.release()
