from spinnman.messages.scp.impl import SDRAMAlloc
from .abstract_multi_connection_process \
    import AbstractMultiConnectionProcess


class MallocSDRAMProcess(AbstractMultiConnectionProcess):
    """ A process for allocating a block of SDRAM on a SpiNNaker chip.
    """
    __slots__ = [
        "_base_address"]

    def __init__(self, connection_selector):
        super(MallocSDRAMProcess, self).__init__(connection_selector)
        self._base_address = None

    def _handle_sdram_alloc_response(self, response):
        self._base_address = response.base_address

    def malloc_sdram(self, x, y, size, app_id, tag):
        # pylint: disable=too-many-arguments
        # Allocate space in the sdram space
        self._send_request(SDRAMAlloc(x, y, app_id, size, tag),
                           self._handle_sdram_alloc_response)
        self._finish()
        self.check_for_error()

    @property
    def base_address(self):
        return self._base_address
