import threading
import collections
import logging
from abc import ABCMeta
from abc import abstractmethod
from six import add_metaclass
import socket

logger = logging.getLogger(__name__)


@add_metaclass(ABCMeta)
class AbstractPortQueuer(threading.Thread):
    """ A Queue for packets received
    """

    def __init__(self):
        threading.Thread.__init__(self)
        self._queue = collections.deque()
        self._queue_condition = threading.Condition()
        self._done = False
        self.setDaemon(True)

    def stop(self):
        """ Stop the thread
        """
        logger.debug("[Queuer] Stopping")
        self._queue_condition.acquire()
        self._done = True
        self._queue_condition.notify_all()
        self._queue_condition.release()

    def run(self):
        logger.debug("[Queuer] Starting")
        while not self._done:
            try:
                packet = self._read_packet()
                self._queue_condition.acquire()
                self._queue.append(packet)
                self._queue_condition.notify_all()
                self._queue_condition.release()
            except socket.timeout:
                pass
            except Exception as e:
                if not self._done:
                    raise e
        self._queue_condition.acquire()
        self._queue_condition.notify_all()
        self._queue_condition.release()

    @abstractmethod
    def _read_packet(self):
        """ Read a packet to be added to the queue

        :return: The read packet
        :raise SpinnmanIOException: If the packet could not be read
        :raise socket.timeout: If there is a timeout on reading
        """

    def get_packet(self):
        """ Get the next packet from the queue

        :return: The next packet, or None if the queue has been stopped
        """
        self._queue_condition.acquire()
        while len(self._queue) == 0 and not self._done:
            self._queue_condition.wait()
        packet = None
        if not self._done:
            packet = self._queue.popleft()
        self._queue_condition.release()
        return packet
