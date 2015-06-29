from abc import ABCMeta
from abc import abstractmethod
from six import add_metaclass

import select
import socket
import struct

from spinnman.connections.abstract_classes.abstract_scp_receiver import \
    AbstractSCPReceiver
from spinnman.exceptions import SpinnmanTimeoutException
from spinnman.exceptions import SpinnmanIOException
from spinnman.messages.scp.scp_result import SCPResult


@add_metaclass(ABCMeta)
class AbstractUDPSCPBMPReceiver(AbstractSCPReceiver):
    """ A receiver of SCP messages
    """

    @abstractmethod
    def is_udp_scp_bmp_receiver(self):
        pass

    def is_ready_to_receive(self):
        return len(select.select([self._socket], [], [], 0)[0]) == 1

    def receive_scp_response(self, timeout=1.0):

        # Receive the data
        raw_data = None
        try:
            self._socket.settimeout(timeout)
            raw_data = self._socket.recv(300)
        except socket.timeout:
            raise SpinnmanTimeoutException("receive_scp_message", timeout)
        except Exception as e:
            raise SpinnmanIOException(str(e))

        result, sequence = struct.unpack_from("2H", raw_data, 10)
        return SCPResult(result), sequence, raw_data, 2
