from __future__ import print_function
import logging
import sys

from spinnman.exceptions import SpinnmanGenericProcessException

logger = logging.getLogger(__name__)


class AbstractProcess(object):
    """ An abstract process for talking to SpiNNaker efficiently
    """

    def __init__(self):
        self._exception = None
        self._traceback = None
        self._error_request = None

    def _receive_error(self, request, exception, tb):
        self._error_request = request
        self._exception = exception
        self._traceback = tb

    def is_error(self):
        return self._exception is not None

    def check_for_error(self, print_exception=False):
        if self._exception is not None:
            exc_info = sys.exc_info()
            if print_exception:
                sdp_header = self._error_request.sdp_header
                logger.error("failure in request to (%d, %d, %d)",
                             sdp_header.destination_chip_x,
                             sdp_header.destination_chip_y,
                             sdp_header.destination_cpu, exc_info=exc_info)
            sdp_header = self._error_request.sdp_header
            self._exception = SpinnmanGenericProcessException(
                self._exception, exc_info[2], sdp_header.destination_chip_x,
                sdp_header.destination_chip_y, sdp_header.destination_cpu)
            raise self._exception, None, self._traceback
