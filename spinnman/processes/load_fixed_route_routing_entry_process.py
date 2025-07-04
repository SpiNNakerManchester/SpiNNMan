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

from spinn_machine import Router, RoutingEntry
from spinnman.messages.scp.impl import FixedRouteInit
from spinnman.processes import AbstractMultiConnectionProcess


class LoadFixedRouteRoutingEntryProcess(AbstractMultiConnectionProcess):
    """
    Load a fixed route routing entry onto a chip.
    """
    __slots__ = ()

    def load_fixed_route(
            self, x: int, y: int, fixed_route: RoutingEntry,
            app_id: int = 0) -> None:
        """
        :param x: The x-coordinate of the chip, between 0 and 255;
            this is not checked due to speed restrictions.
        :param y: The y-coordinate of the chip, between 0 and 255;
            this is not checked due to speed restrictions.
        :param fixed_route: the fixed route entry
        :param app_id: The ID of the application with which to associate
            the routes.  If not specified, defaults to 0.
        """
        route_entry = Router.convert_routing_table_entry_to_spinnaker_route(
            fixed_route)
        with self._collect_responses():
            self._send_request(FixedRouteInit(x, y, route_entry, app_id))
