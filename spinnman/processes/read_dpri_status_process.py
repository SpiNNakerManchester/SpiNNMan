from spinnman.processes.\
    multi_connection_process_most_direct_connection_selector \
    import MultiConnectionProcessMostDirectConnectionSelector
from spinnman.messages.scp.impl.scp_dpri_get_status_request \
    import SCPDPRIGetStatusRequest
from spinnman.processes.abstract_multi_connection_process \
    import AbstractMultiConnectionProcess


class ReadDPRIStatusProcess(AbstractMultiConnectionProcess):

    def __init__(self, machine, connections):
        AbstractMultiConnectionProcess.__init__(
            self, connections,
            MultiConnectionProcessMostDirectConnectionSelector(
                machine, connections))
        self._dpri_status = None

    def handle_dpri_status_response(self, response):
        self._dpri_status = response.dpri_status

    def get_dpri_status(self, x, y, p):
        self._send_request(SCPDPRIGetStatusRequest(x, y, p),
                           callback=self.handle_dpri_status_response)
        self._finish()
        self.check_for_error()
        return self._dpri_status
