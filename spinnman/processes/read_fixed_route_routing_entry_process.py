from spinnman.messages.scp.impl.fixed_route_read import FixedRouteRead
from spinnman.processes import AbstractMultiConnectionProcess


class ReadFixedRouteRoutingEntryProcess(AbstractMultiConnectionProcess):
    """ A process for reading a chip's fixed route routing entry.
    """

    __slots__ = (
        # the fixed route routing entry from the response
        "_route",
    )

    def __init__(self, connection_selector):
        """ Creates the process for writing a fixed route entry to a chip's\
            router

        :param connection_selector: the SC&MP connection selector
        """
        super(ReadFixedRouteRoutingEntryProcess, self).__init__(
            connection_selector)
        self._route = None

    def handle_read_response(self, response):
        self._route = response.route

    def read_fixed_route(self, x, y, app_id=0):
        """ Deads a fixed route routing table entry

        :param x: The x-coordinate of the chip, between 0 and 255, \
            this is not checked due to speed restrictions
        :type x: int
        :param y: The y-coordinate of the chip, between 0 and 255\
            this is not checked due to speed restrictions
        :type y: int
        :param app_id: The id of the application with which to associate the\
            routes.  If not specified, defaults to 0.
        :type app_id: int
        :rtype: None
        """
        self._send_request(FixedRouteRead(x, y, app_id),
                           self.handle_read_response)
        self._finish()
        self.check_for_error()
        return self._route
