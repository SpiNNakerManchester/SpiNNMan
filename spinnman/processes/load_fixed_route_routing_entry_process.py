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

from spinn_machine import Router
from spinnman.messages.scp.impl.fixed_route_init import FixedRouteInit
from spinnman.processes import AbstractMultiConnectionProcess


class LoadFixedRouteRoutingEntryProcess(AbstractMultiConnectionProcess):
    __slots__ = []

    def load_fixed_route(self, x, y, fixed_route, app_id=0):
        """ Load a fixed route routing entry onto a chip.

        :param x: The x-coordinate of the chip, between 0 and 255; \
            this is not checked due to speed restrictions.
        :type x: int
        :param y: The y-coordinate of the chip, between 0 and 255; \
            this is not checked due to speed restrictions.
        :type y: int
        :param fixed_route: the fixed route entry
        :param app_id: The ID of the application with which to associate the\
            routes.  If not specified, defaults to 0.
        :type app_id: int
        :rtype: None
        """
        route_entry = \
            Router.convert_routing_table_entry_to_spinnaker_route(fixed_route)
        self._send_request(FixedRouteInit(x, y, route_entry, app_id))
        self._finish()
        self.check_for_error()
