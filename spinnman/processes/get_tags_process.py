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

import functools
from spinn_machine.tags import ReverseIPTag, IPTag
from .abstract_multi_connection_process import AbstractMultiConnectionProcess
from spinnman.messages.scp.impl import IPTagGetInfo, IPTagGet


class GetTagsProcess(AbstractMultiConnectionProcess):
    __slots__ = [
        "_tags",
        "_tag_info"]

    def __init__(self, connection_selector):
        """
        :param connection_selector:
        :type connection_selector:
            AbstractMultiConnectionProcessConnectionSelector
        """
        super().__init__(connection_selector)
        self._tag_info = None
        self._tags = None

    def __handle_tag_info_response(self, response):
        self._tag_info = response

    def __handle_get_tag_response(self, tag, board_address, response):
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

    def get_tags(self, connection):
        """
        :param SCAMPConnection connection:
        :rtype:
            list(~spinn_machine.tags.IPTag or ~spinn_machine.tags.ReverseIPTag)
        """
        # Get the tag information, without which we cannot continue
        self._send_request(IPTagGetInfo(
            connection.chip_x, connection.chip_y),
            self.__handle_tag_info_response)
        self._finish()
        self.check_for_error()

        # Get the tags themselves
        n_tags = self._tag_info.pool_size + self._tag_info.fixed_size
        self._tags = [None] * n_tags
        for tag in range(n_tags):
            self._send_request(IPTagGet(
                connection.chip_x, connection.chip_y, tag),
                functools.partial(
                    self.__handle_get_tag_response, tag,
                    connection.remote_ip_address))
        self._finish()
        self.check_for_error()

        # Return the tags
        return [tag for tag in self._tags if tag is not None]
