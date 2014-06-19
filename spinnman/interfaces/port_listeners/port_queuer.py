__author__ = 'stokesa6'
import threading
import thread
import collections
import socket
import logging
logger = logging.getLogger(__name__)


def _timeout(visualiser):
    visualiser.stop()


class _PortQueuer(threading.Thread):
    """thread that holds a queue to try to stop the loss of packets from the \
       socket"""

    def __init__(self):
        """constructor for a port_queuer object

        :return: a new port_Queuer object
        :rtype: spinnman.interfaces.port_listeners.port_queuer.PortQueuer
        :raise None: does not raise any known exceptions
        """
        threading.Thread.__init__(self)
        self.queue = collections.deque()
        self.bufsize = 65536
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(1)
        self.done = False
        self.exited = False

    def set_timeout(self, timeout):
        """supports changing how long to timeout

        :param timeout: the associated length of time for a timeout
        :type timeout: int
        :return: None
        :rtype: None
        :raise None:  does not raise any known exceptions
        """
        print("Timeout set to %f" % timeout)
        if timeout > 0:
            thread.start_new_thread(_timeout, (self, timeout))

    def set_bufsize(self, bufsize):
        """supports changing of the bufsize

        :param bufsize: the associated new bufsize
        :type bufsize: int
        :return: None
        :rtype: None
        :raise None:  does not raise any known exceptions
        """
        self.bufsize = bufsize

    def set_port(self, port):
        """sets the queuer port

        :return: None
        :rtype: None
        :raise None:   does not raise any known exceptions
        """
        try:
            self.sock.bind(("0.0.0.0", port))
        except socket.error as e:
            if e.errno == 98:
                logger.error("socket already in use, "
                             "please close all other spinn_views")
            else:
                logger.error(e.message)
        print

    def stop(self):
        """stops the port queuer
        :return: None
        :rtype: None
        :raise None:   does not raise any known exceptions
        """
        logger.info("[queuer] Stopping")
        self.done = True
        while not self.exited:
            pass
        try:
            self.sock.shutdown(socket.SHUT_RDWR)
        except Exception as e:
            logger.warn("tries to close a non-connected socket, "
                        "ignoring and continuing")
            return 0
        self.sock.close()

    def run(self):
        """opening method for this thread

        :return: None
        :rtype: None
        :raise None:   does not raise any known exceptions

        """
        logger.info("[port_queuer] starting")
        while not self.done:
            try:
                data, addr = self.sock.recvfrom(self.bufsize)
                self.queue.append(data)
            except socket.timeout:
                pass
        self.exited = True

    def get_packet(self):
        """allows the port listener to pull a packet from the non-blocking queue

        :return: a new packet thast been recieved
        :rtype: SCP packet
        :raise None: does not raise any known exceptions
        """
        got = False
        packet = None
        while not got:
            if len(self.queue) != 0:

                packet = self.queue.popleft()
                got = True
        return packet

