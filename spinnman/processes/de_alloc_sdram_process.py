from spinnman.messages.scp.impl import SDRAMDeAlloc
from .abstract_multi_connection_process import AbstractMultiConnectionProcess


class DeAllocSDRAMProcess(AbstractMultiConnectionProcess):
    __slots__ = [
        "_no_blocks_freed"]

    def __init__(self, connection_selector):
        super(DeAllocSDRAMProcess, self).__init__(connection_selector)
        self._no_blocks_freed = None

    def de_alloc_sdram(self, x, y, app_id, base_address=None):
        callback = None
        # deallocate space in the SDRAM
        if base_address is None:
            callback = self._handle_sdram_alloc_response
        self._send_request(SDRAMDeAlloc(x, y, app_id, base_address),
                           callback=callback)
        self._finish()
        self.check_for_error()

    def _handle_sdram_alloc_response(self, response):
        self._no_blocks_freed = response.number_of_blocks_freed

    @property
    def no_blocks_freed(self):
        return self._no_blocks_freed
