# Copyright (c) 2017 The University of Manchester
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

from spinnman.messages.scp.impl.fixed_route_read import FixedRouteRead
from .abstract_multi_connection_process import AbstractMultiConnectionProcess


class ReadFixedRouteRoutingEntryProcess(AbstractMultiConnectionProcess):
    """
    A process for reading a fixed route routing table entry.
    """

    __slots__ = (
        # the fixed route routing entry from the response
        "_route",
    )

    def __init__(self, connection_selector):
        """
        :param connection_selector: the SC&MP connection selector
        :type connection_selector:
            AbstractMultiConnectionProcessConnectionSelector
        """
        super().__init__(connection_selector)
        self._route = None

    def __handle_read_response(self, response):
        self._route = response.route

    def read_fixed_route(self, x, y, app_id=0):
        """
        Read the fixed route entry installed on a particular chip's router.

        :param int x: The x-coordinate of the chip, between 0 and 255;
            this is not checked due to speed restrictions
        :param int y: The y-coordinate of the chip, between 0 and 255;
            this is not checked due to speed restrictions
        :param int app_id:
            The ID of the application with which to associate the
            routes.  If not specified, defaults to 0.
        :rtype: ~spinn_machine.FixedRouteEntry
        """
        self._send_request(FixedRouteRead(x, y, app_id),
                           self.__handle_read_response)
        self._finish()
        self.check_for_error()
        return self._route
