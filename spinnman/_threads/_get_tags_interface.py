from threading import Condition
import sys
import logging

from _scp_message_interface import SCPMessageInterface
from spinnman.messages.scp.impl.scp_iptag_info_request \
    import SCPTagInfoRequest
from spinnman.messages.scp.impl.scp_iptag_get_request import SCPTagGetRequest


from spinn_machine.tags.iptag import IPTag
from spinn_machine.tags.reverse_iptag import ReverseIPTag

logger = logging.getLogger(__name__)


class GetTagsInterface(object):
    """ A thread for reading the IP Tags from a UDPConnection
    """

    def __init__(self, transceiver, connection, thread_pool):
        """

        :param transceiver: The transceiver to use to send the message
        :type transceiver: :py:class:`spinnman.transceiver.Transceiver`
        :param connection: The UDP connection from which the tags are to\
                    be retrieved
        :type connection:\
                    :py:class:`spinnman.connections.udp_connection.UDPConnection`
        :raise None: No known exceptions are thrown
        """
        self._transceiver = transceiver
        self._connection = connection
        self._exception = None
        self._traceback = None
        self._tags = None
        self._condition = Condition()
        self._thread_pool = thread_pool

    def run(self):
        """ Run method of the thread.  Note callers should call start() to\
            actually run this in a separate thread.
        """
        try:
            get_info_thread = SCPMessageInterface(
                self._transceiver, SCPTagInfoRequest(
                    self._connection.chip_x, self._connection.chip_y))
            self._thread_pool.apply_async(get_info_thread.run)
            info = get_info_thread.get_response()

            threads = list()
            tags = dict()
            for tag in range(0, info.pool_size + info.fixed_size):
                thread = SCPMessageInterface(
                    self._transceiver, SCPTagGetRequest(
                        self._connection.chip_x, self._connection.chip_y, tag))
                self._thread_pool.apply_async(thread.run)
                threads.append(thread)
                tags[thread] = tag

            tags = list()
            for thread in threads:
                response = thread.get_response()
                tag = tags[thread]
                if response.in_use:
                    ip_address = response.ip_address
                    host = "{}.{}.{}.{}"\
                        .format(ip_address[0], ip_address[1], ip_address[2],
                                ip_address[3])
                    if response.is_reverse:
                        tags.append(ReverseIPTag(
                            self._connection.remote_ip_address, tag,
                            response.rx_port, response.spin_chip_x,
                            response.spin_chip_y, response.spin_cpu,
                            response.spin_port))
                    else:
                        tags.append(IPTag(
                            self._connection.remote_ip_address,
                            tag, host, response.port, response.strip_sdp))

            self._condition.acquire()
            self._tags = tags
            self._condition.notify_all()
            self._condition.release()

        except Exception as exception:
            self._condition.acquire()
            self._exception = exception
            self._traceback = sys.exc_info()[2]
            self._condition.notify_all()
            self._condition.release()

    def get_tags(self):
        """ Get the ip tags retrieved.  This will\
            block until the value has been retrieved
        """
        self._condition.acquire()
        while self._tags is None and self._exception is None:
            self._condition.wait()
        self._condition.release()

        if self._exception is not None:
            raise self._exception, None, self._traceback

        return self._tags
