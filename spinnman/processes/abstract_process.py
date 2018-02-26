from __future__ import print_function
import logging
import sys

from spinnman.exceptions import SpinnmanGenericProcessException, \
    SpinnmanGroupedProcessException

logger = logging.getLogger(__name__)


class AbstractProcess(object):
    """ An abstract process for talking to SpiNNaker efficiently
    """
    __slots__ = [
        "_error_request",
        "_exception",
        "_traceback"]

    def __init__(self):
        self._exceptions = list()
        self._tracebacks = list()
        self._error_requests = list()

    def _receive_error(self, request, exception, tb):
        self._error_requests.append(request)
        self._exceptions.append(exception)
        self._tracebacks.append(tb)

    def is_error(self):
        return self._exceptions is not None

    def check_for_error(self, print_exception=False):

        if len(self._exceptions) != 0:
            if len(self._exceptions) == 1:
                exc_info = sys.exc_info()

                if print_exception:
                    sdp_header = self._error_requests[0].sdp_header
                    logger.error("failure in request to (%d, %d, %d)",
                                 sdp_header.destination_chip_x,
                                 sdp_header.destination_chip_y,
                                 sdp_header.destination_cpu, exc_info=exc_info)

                sdp_header = self._error_requests[0].sdp_header
                this_exception = SpinnmanGenericProcessException(
                    self._exceptions[0], exc_info[2],
                    sdp_header.destination_chip_x,
                    sdp_header.destination_chip_y, sdp_header.destination_cpu)
                raise this_exception, None, self._tracebacks[0]
            else:
                this_exception = SpinnmanGroupedProcessException(
                    self._error_requests, self._exceptions, self._tracebacks)
                if print_exception:
                    logger.error(this_exception.message, this_exception.args)
                raise this_exception, None, None
