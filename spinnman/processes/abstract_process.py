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

from __future__ import print_function
import logging
import sys
from spinnman.exceptions import (
    SpinnmanGenericProcessException, SpinnmanGroupedProcessException)

logger = logging.getLogger(__name__)


class AbstractProcess(object):
    """ An abstract process for talking to SpiNNaker efficiently.
    """
    __slots__ = [
        "_error_requests",
        "_exceptions",
        "_tracebacks"]

    def __init__(self):
        self._exceptions = []
        self._tracebacks = []
        self._error_requests = []

    def _receive_error(self, request, exception, tb):
        self._error_requests.append(request)
        self._exceptions.append(exception)
        self._tracebacks.append(tb)

    def is_error(self):
        return bool(self._exceptions)

    def check_for_error(self, print_exception=False):
        if len(self._exceptions) == 1:
            exc_info = sys.exc_info()
            sdp_header = self._error_requests[0].sdp_header

            if print_exception:
                logger.error("failure in request to (%d, %d, %d)",
                             sdp_header.destination_chip_x,
                             sdp_header.destination_chip_y,
                             sdp_header.destination_cpu,
                             exc_info=(Exception, self._exceptions,
                                       self._tracebacks))

            raise SpinnmanGenericProcessException(
                self._exceptions[0], exc_info[2],
                sdp_header.destination_chip_x,
                sdp_header.destination_chip_y, sdp_header.destination_cpu,
                self._tracebacks[0])
        elif self._exceptions:
            ex = SpinnmanGroupedProcessException(
                self._error_requests, self._exceptions, self._tracebacks)
            if print_exception:
                logger.error("%s", str(ex))
            raise ex
