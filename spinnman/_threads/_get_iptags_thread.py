from threading import Thread
from threading import Condition

from spinnman._threads._scp_message_thread import _SCPMessageThread
from spinnman.messages.scp.impl.scp_iptag_info_request import SCPIPTagInfoRequest
from spinnman.messages.scp.impl.scp_iptag_get_request import SCPIPTagGetRequest
from spinnman.model.iptag.iptag import IPTag

import sys
import logging
from spinnman.model.iptag.reverse_iptag import ReverseIPTag

logger = logging.getLogger(__name__)


class _GetIPTagsThread(Thread):
    """ A thread for reading the IP Tags from a UDPConnection
    """

    def __init__(self, transceiver, connection):
        """

        :param transceiver: The transceiver to use to send the message
        :type transceiver: :py:class:`spinnman.transceiver.Transceiver`
        :param connection: The UDP connection from which the tags are to\
                    be retrieved
        :type connection:\
                    :py:class:`spinnman.connections.udp_connection.UDPConnection`
        :raise None: No known exceptions are thrown
        """
        super(_GetIPTagsThread, self).__init__()
        self._transceiver = transceiver
        self._connection = connection
        self._exception = None
        self._traceback = None
        self._iptags = None
        self._condition = Condition()
        self.setDaemon(True)

    def run(self):
        """ Run method of the thread.  Note callers should call start() to\
            actually run this in a separate thread.
        """
        try:
            get_info_thread = _SCPMessageThread(
                    self._transceiver,
                    SCPIPTagInfoRequest(
                            self._connection.chip_x, self._connection.chip_y),
                    connection=self._connection)
            get_info_thread.start()
            info = get_info_thread.get_response()

            threads = list()
            tags = dict()
            for tag in range(0, info.pool_size + info.fixed_size):
                thread = _SCPMessageThread(
                        self._transceiver,
                        SCPIPTagGetRequest(
                                self._connection.chip_x,
                                self._connection.chip_y,
                                tag),
                        connection=self._connection)
                thread.start()
                threads.append(thread)
                tags[thread] = tag

            iptags = list()
            for thread in threads:
                response = thread.get_response()
                tag = tags[thread]
                if response.in_use:
                    ip_address = response.ip_address
                    host = "{}.{}.{}.{}".format(ip_address[0], ip_address[1],
                            ip_address[2], ip_address[3])
                    if response.is_reverse:
                        iptags.append(ReverseIPTag(response.rx_port, tag,
                                response.spin_chip_x, response.spin_chip_y,
                                response.spin_cpu, response.spin_port))
                    else:
                        iptags.append(IPTag(host, response.port, tag,
                                strip_sdp=response.strip_sdp))


            self._condition.acquire()
            self._iptags = iptags
            self._condition.notify_all()
            self._condition.release()

        except Exception as exception:
            self._condition.acquire()
            self._exception = exception
            self._traceback = sys.exc_info()[2]
            self._condition.notify_all()
            self._condition.release()

    def get_iptags(self):
        """ Get the ip tags retrieved.  This will\
            block until the value has been retrieved
        """
        self._condition.acquire()
        while self._iptags is None and self._exception is None:
            self._condition.wait()
        self._condition.release()

        if self._exception is not None:
            raise self._exception, None, self._traceback

        return self._iptags
