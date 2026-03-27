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

from functools import partial
from typing import List, Optional

from spinn_machine.tags import AbstractTag, ReverseIPTag, IPTag

from spinnman.messages.scp.impl.iptag_get import IPTagGet, IPTagGetResponse
from spinnman.messages.scp.impl.iptag_get_info import IPTagGetInfo
from spinnman.messages.scp.impl.iptag_get_info_response import (
    IPTagGetInfoResponse)
from spinnman.connections.udp_packet_connections import SCAMPConnection

from .abstract_multi_connection_process import AbstractMultiConnectionProcess
from .abstract_multi_connection_process_connection_selector import (
    ConnectionSelector)


class GetTagsProcess(AbstractMultiConnectionProcess):
    """
    Gets information about the tags over the provided connection.
    """
    __slots__ = (
        "_tags",
        "_tag_info")

    def __init__(self, connection_selector: ConnectionSelector):
        """
        :param connection_selector:
        """
        super().__init__(connection_selector)
        self._tag_info: Optional[IPTagGetInfoResponse] = None
        self._tags: List[Optional[AbstractTag]] = []

    def __handle_tag_info_response(
            self, response: IPTagGetInfoResponse) -> None:
        self._tag_info = response

    def __handle_get_tag_response(self, tag: int, board_address: str,
                                  response: IPTagGetResponse) -> None:
        if response.in_use:
            ip = response.ip_address
            host = f"{ip[0]}.{ip[1]}.{ip[2]}.{ip[3]}"
            if response.is_reverse:
                self._tags[tag] = ReverseIPTag(
                    board_address, tag,
                    response.rx_port, response.spin_chip_x,
                    response.spin_chip_y, response.spin_cpu,
                    response.spin_port)
            else:
                self._tags[tag] = IPTag(
                    board_address, response.sdp_header.source_chip_x,
                    response.sdp_header.source_chip_y, tag, host,
                    response.port, response.strip_sdp)

    def get_tags(self, connection: SCAMPConnection) -> List[AbstractTag]:
        """
        :param connection:
        :returns: The tags read from the connection.
        """
        # Get the tag information, without which we cannot continue
        with self._collect_responses():
            self._send_request(IPTagGetInfo(
                connection.chip_x, connection.chip_y),
                self.__handle_tag_info_response)
        assert self._tag_info is not None

        # Get the tags themselves
        n_tags = self._tag_info.pool_size + self._tag_info.fixed_size
        self._tags = [None] * n_tags
        with self._collect_responses():
            board_address = connection.remote_ip_address
            assert board_address is not None
            for tag in range(n_tags):
                self._send_request(IPTagGet(
                    connection.chip_x, connection.chip_y, tag),
                    partial(
                        self.__handle_get_tag_response, tag,
                        board_address))

        # Return the tags
        return [tag for tag in self._tags if tag is not None]
