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

import logging
import sys
from spinn_utilities.abstract_base import (
    AbstractBase, abstractproperty)
from spinn_utilities.log import FormatAdapter
from spinnman.exceptions import (
    SpinnmanGenericProcessException, SpinnmanGroupedProcessException,
    get_physical_cpu_id)

logger = FormatAdapter(logging.getLogger(__name__))


class AbstractProcess(object, metaclass=AbstractBase):
    """ An abstract process for talking to SpiNNaker efficiently.
    """
    __slots__ = [
        "_error_requests",
        "_exceptions",
        "_tracebacks",
        "_connections", ]

    ERROR_MESSAGE = (
        "failure in request to board {} with ethernet chip (%d, %d) for "
        "chip (%d, %d, %d%s")

    def __init__(self):
        self._exceptions = []
        self._tracebacks = []
        self._error_requests = []
        self._connections = []

    def _receive_error(self, request, exception, tb, connection):
        self._error_requests.append(request)
        self._exceptions.append(exception)
        self._tracebacks.append(tb)
        self._connections.append(connection)

    def is_error(self):
        return bool(self._exceptions)

    @abstractproperty
    def connection_selector(self):
        """ Get the connection selector of the process
        """

    def check_for_error(self, print_exception=False):
        if len(self._exceptions) == 1:
            exc_info = sys.exc_info()
            sdp_header = self._error_requests[0].sdp_header

            phys_p = get_physical_cpu_id(
                self.connection_selector.machine, sdp_header)

            if print_exception:
                connection = self._connections[0]
                logger.error(
                    self.ERROR_MESSAGE.format(
                        connection.remote_ip_address, connection.chip_x,
                        connection.chip_y, sdp_header.destination_chip_x,
                        sdp_header.destination_chip_y,
                        sdp_header.destination_cpu, phys_p))

            raise SpinnmanGenericProcessException(
                self._exceptions[0], exc_info[2],
                sdp_header.destination_chip_x,
                sdp_header.destination_chip_y, sdp_header.destination_cpu,
                phys_p, self._tracebacks[0])
        elif self._exceptions:
            ex = SpinnmanGroupedProcessException(
                self._error_requests, self._exceptions, self._tracebacks,
                self._connections, self.connection_selector.machine)
            if print_exception:
                logger.error("{}".format(str(ex)))
            raise ex
