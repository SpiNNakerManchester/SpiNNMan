# Copyright (c) 2017-2019 The University of Manchester
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import functools
from past.builtins import xrange
from .abstract_multi_connection_process import AbstractMultiConnectionProcess
from spinnman.messages.scp.impl import IPTagGetInfo, IPTagGet


class GetTagsProcess(AbstractMultiConnectionProcess):
    __slots__ = [
        "_tags",
        "_tag_info"]

    def __init__(self, connection_selector):
        super(GetTagsProcess, self).__init__(connection_selector)
        self._tag_info = None
        self._tags = None

    def handle_tag_info_response(self, response):
        self._tag_info = response

    def handle_get_tag_response(self, tag, response):
        if response.in_use:
            self._tags[tag] = response

    def get_tags(self, connection):
        # Get the tag information, without which we cannot continue
        self._send_request(IPTagGetInfo(
            connection.chip_x, connection.chip_y),
            self.handle_tag_info_response)
        self._finish()
        self.check_for_error()

        # Get the tags themselves
        n_tags = self._tag_info.pool_size + self._tag_info.fixed_size
        self._tags = [None] * n_tags
        for tag in xrange(n_tags):
            self._send_request(IPTagGet(
                connection.chip_x, connection.chip_y, tag),
                functools.partial(
                    self.handle_get_tag_response, tag))
        self._finish()
        self.check_for_error()

        # Return the tags
        return self._tags
