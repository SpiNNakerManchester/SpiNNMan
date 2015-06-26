from spinnman.processes.abstract_multi_connection_process\
    import AbstractMultiConnectionProcess
from spinnman.processes\
    .multi_connection_process_most_direct_connection_selector\
    import MultiConnectionProcessMostDirectConnectionSelector


class SendSingleCommandProcess(AbstractMultiConnectionProcess):

    def __init__(self, machine, connections, connection_selector=None):
        if connection_selector is None:
            connection_selector = \
                MultiConnectionProcessMostDirectConnectionSelector(
                    machine, connections)
        AbstractMultiConnectionProcess.__init__(
            self, connections, connection_selector)
        self._response = None

    def handle_response(self, response):
        self._response = response

    def execute(self, request):
        self._send_request(request, self.handle_response)
        self._finish()
        self.check_for_error()
        return self._response
