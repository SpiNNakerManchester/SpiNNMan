from __future__ import print_function
import sys


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
                print(self._exception, file=sys.stderr)
                print(self._traceback_info, file=sys.stderr)
            raise self._exception
