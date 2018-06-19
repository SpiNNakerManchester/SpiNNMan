from spinn_machine import Router
from spinnman.messages.scp.impl.fixed_route_init import FixedRouteInit
from spinnman.processes import AbstractMultiConnectionProcess


class LoadFixedRouteRoutingEntryProcess(AbstractMultiConnectionProcess):
    __slots__ = []

    def load_fixed_route(self, x, y, fixed_route, app_id=0):
        """ Load a fixed route routing entry onto a chip

        :param x: The x-coordinate of the chip, between 0 and 255, \
            this is not checked due to speed restrictions
        :type x: int
        :param y: The y-coordinate of the chip, between 0 and 255\
            this is not checked due to speed restrictions
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
