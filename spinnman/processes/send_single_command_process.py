from .abstract_multi_connection_process import AbstractMultiConnectionProcess
from spinnman.constants import SCP_TIMEOUT


class SendSingleCommandProcess(AbstractMultiConnectionProcess):
    __slots__ = [
        "_response"]

    def __init__(self, connection_selector, n_retries=3, timeout=SCP_TIMEOUT):
        super(SendSingleCommandProcess, self).__init__(
            connection_selector, n_retries=n_retries, timeout=timeout)
        self._response = None

    def handle_response(self, response):
        self._response = response

    def execute(self, request):
        self._send_request(request, self.handle_response)
        self._finish()
        self.check_for_error()
        return self._response
