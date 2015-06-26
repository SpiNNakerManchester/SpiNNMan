from __future__ import print_function
import sys
import traceback


class AbstractProcess(object):
    """ An abstract process for talking to SpiNNaker efficiently
    """

    def __init__(self):
        self._exception = None
        self._traceback_info = None

    def _receive_error(self, request, exception, tracebackinfo):
        self._exception = exception
        self._traceback_info = tracebackinfo

    def is_error(self):
        return self._exception is not None

    def check_for_error(self, print_exception=True):
        if self._exception is not None:
            if print_exception:
                for line in traceback.format_exception_only(
                        self._exception.__class__, self._exception):
                    print(line, end="", file=sys.stderr)
                for line in traceback.format_list(self._traceback_info):
                    print(line, end="", file=sys.stderr)
            raise self._exception
