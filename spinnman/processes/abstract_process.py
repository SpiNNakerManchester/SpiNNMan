from __future__ import print_function

from spinnman import exceptions

import sys
import traceback


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
            if print_exception:
                sdp_header = self._error_request.sdp_header
                print("Error in request to {}, {}, {}".format(
                    sdp_header.destination_chip_x,
                    sdp_header.destination_chip_y,
                    sdp_header.destination_cpu),
                    file=sys.stderr)
                for line in traceback.format_exception_only(
                        self._exception.__class__, self._exception):
                    print(line, end="", file=sys.stderr)
                for line in traceback.format_tb(self._traceback):
                    print(line, end="", file=sys.stderr)

            exc_info = sys.exc_info()
            sdp_header = self._error_request.sdp_header
            self._exception = exceptions.SpinnmanGenericProcessException(
                self._exception, exc_info[2], sdp_header.destination_chip_x,
                sdp_header.destination_chip_y, sdp_header.destination_cpu)
            raise self._exception, None, self._traceback
