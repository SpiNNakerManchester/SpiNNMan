from __future__ import print_function
import sys
import traceback


class AbstractProcess(object):
    """ An abstract process for talking to SpiNNaker efficiently
    """

    def __init__(self):
        self._exception = None
        self._traceback = None

    def _receive_error(self, request, exception, tb):
        self._exception = exception
        self._traceback = tb

    def is_error(self):
        return self._exception is not None

    def check_for_error(self, print_exception=False):
        if self._exception is not None:
            if print_exception:
                for line in traceback.format_exception_only(
                        self._exception.__class__, self._exception):
                    print(line, end="", file=sys.stderr)
                for line in traceback.format_tb(self._traceback):
                    print(line, end="", file=sys.stderr)
            raise self._exception, None, self._traceback
