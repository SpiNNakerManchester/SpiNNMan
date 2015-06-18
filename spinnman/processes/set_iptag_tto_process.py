from spinnman.messages.scp.impl.scp_iptag_tto_request import SCPIPTagTTORequest
from spinnman.processes.abstract_single_connection_process \
    import AbstractSingleConnectionProcess


class SetIPTagTTOProcess(AbstractSingleConnectionProcess):
    """ A process for setting the IPTag TTO of the machine
    """

    def __init__(self, connection):
        AbstractSingleConnectionProcess.__init__(self, connection)
        self._previous_tto = None

    def _get_response(self, iptag_response):
        self._previous_tto = iptag_response.transient_timeout
        print self._previous_tto

    def set_tto(self, x, y, tto):
        self._send_request(SCPIPTagTTORequest(x, y, tto),
                           self._get_response)
        self._finish()
        self.check_for_error()
        return self._previous_tto
