from spinnman.messages.scp.impl import ApplicationRun
from .abstract_multi_connection_process import AbstractMultiConnectionProcess


class ApplicationRunProcess(AbstractMultiConnectionProcess):

    def __init__(self, connection_selector):
        AbstractMultiConnectionProcess.__init__(
            self, connection_selector)

    def run(self, app_id, core_subsets, wait):
        for core_subset in core_subsets:
            x = core_subset.x
            y = core_subset.y
            self._send_request(
                ApplicationRun(
                    app_id, x, y, core_subset.processor_ids, wait))
        self._finish()
        self.check_for_error()
