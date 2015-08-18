from spinnman.processes\
    .multi_connection_process_most_direct_connection_selector \
    import MultiConnectionProcessMostDirectConnectionSelector
from spinnman.messages.scp.impl.scp_dpri_reset_counters_request \
    import SCPDPRIResetCountersRequest
from spinnman.processes.abstract_multi_connection_process \
    import AbstractMultiConnectionProcess


class ResetDPRICountersProcess(AbstractMultiConnectionProcess):

    def __init__(self, machine, connections):
        AbstractMultiConnectionProcess.__init__(
            self, connections,
            MultiConnectionProcessMostDirectConnectionSelector(
                machine, connections))
        self._connections = connections

    def reset_counters(self, core_subsets):
        for core_subset in core_subsets.core_subsets:
            for processor_id in core_subset.processor_ids:
                self._send_request(SCPDPRIResetCountersRequest(
                    core_subset.x, core_subset.y, processor_id))
        self._finish()
        self.check_for_error()
