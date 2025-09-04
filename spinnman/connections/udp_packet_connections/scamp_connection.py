# Copyright (c) 2015 The University of Manchester
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import struct
from typing import Optional, Tuple
from spinn_utilities.overrides import overrides
from spinnman.constants import SCP_SCAMP_PORT
from spinnman.messages.scp.enums import SCPResult
from spinnman.connections.abstract_classes import AbstractSCPConnection
from spinnman.messages.scp.abstract_messages import AbstractSCPRequest
from .sdp_connection import SDPConnection

_TWO_SHORTS = struct.Struct("<2H")
_TWO_SKIP = struct.Struct("<2x")


class SCAMPConnection(SDPConnection, AbstractSCPConnection):
    """
    A UDP connection to SCAMP on the board.
    """
    __slots__ = ()

    def __init__(
            self, chip_x: int = 255, chip_y: int = 255,
            local_host: Optional[str] = None,
            local_port: Optional[int] = None,
            remote_host: Optional[str] = None,
            remote_port: Optional[int] = None):
        """
        :param chip_x:
            The x-coordinate of the chip on the board with this remote_host
        :param chip_y:
            The y-coordinate of the chip on the board with this remote_host
        :param local_host: The optional IP address or host name of the
            local interface to listen on
        :param local_port: The optional local port to listen on
        :param remote_host: The optional remote host name or IP address to
            send messages to.  If not specified, sending will not be possible
            using this connection
        :param remote_port: The optional remote port number to send
            messages to. If not specified, sending will not be possible using
            this connection
        """
        if remote_port is None:
            remote_port = SCP_SCAMP_PORT
        super().__init__(
            chip_x, chip_y, local_host, local_port, remote_host, remote_port)

    @property
    @overrides(AbstractSCPConnection.chip_x)
    def chip_x(self) -> int:
        return self._chip_x

    @property
    @overrides(AbstractSCPConnection.chip_y)
    def chip_y(self) -> int:
        return self._chip_y

    def update_chip_coordinates(self, x: int, y: int) -> None:
        """
        Sets the coordinates without checking they are valid.

        :param x:
        :param y:
        """
        self._chip_x = x
        self._chip_y = y

    @overrides(AbstractSCPConnection.get_scp_data)
    def get_scp_data(
            self, scp_request: AbstractSCPRequest,
            x: Optional[int] = None, y: Optional[int] = None) -> bytes:
        """
        :param x: Optional: x-coordinate of where to send to
        :param y: Optional: y-coordinate of where to send to
        """
        if x is None:
            x = self.chip_x
        if y is None:
            y = self.chip_y
        scp_request.sdp_header.update_for_send(x, y)
        return _TWO_SKIP.pack() + scp_request.bytestring

    @overrides(AbstractSCPConnection.receive_scp_response)
    def receive_scp_response(self, timeout: Optional[float] = 1.0) -> Tuple[
            SCPResult, int, bytes, int]:
        data = self.receive(timeout)
        result, sequence = _TWO_SHORTS.unpack_from(data, 10)
        return SCPResult(result), sequence, data, 2

    def receive_scp_response_with_address(
            self, timeout: float = 1.0) -> Tuple[
                SCPResult, int, bytes, int, str, int]:
        """
        Receive data from the connection along with the address where the
        data was received from.

        :param timeout: The timeout, or `None` to wait forever

        :returns:   A tuple of SCPResult, sequence number, the data received
            the number2, IP address  and port used.
        """
        data, (addr, port) = self.receive_with_address(timeout)
        result, sequence = _TWO_SHORTS.unpack_from(data, 10)
        return SCPResult(result), sequence, data, 2, addr, port

    def __repr__(self) -> str:
        return (
            f"SCAMPConnection(chip_x={self._chip_x}, chip_y={self._chip_y}, "
            f"local_host={self.local_ip_address}, local_port={self.local_port}"
            f", remote_host={self.remote_ip_address}, "
            f"remote_port={self.remote_port})")
