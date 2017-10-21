from spinnman.processes import AbstractMultiConnectionProcess
from spinnman import constants
from spinnman.model.heap_element import HeapElement
from spinnman.messages.spinnaker_boot import SystemVariableDefinition
from spinnman.messages.scp.impl import ReadMemory

import struct
import functools

HEAP_ADDRESS = SystemVariableDefinition.sdram_heap_address


class GetHeapProcess(AbstractMultiConnectionProcess):

    def __init__(self, connection_selector):
        AbstractMultiConnectionProcess.__init__(self, connection_selector)

        self._heap_address = None
        self._next_block_address = None
        self._blocks = list()

    def _read_heap_address_response(self, response):
        self._heap_address = struct.unpack_from(
            "<I", response.data, response.offset)[0]

    def _read_heap_pointer(self, response):
        self._next_block_address = struct.unpack_from(
            "<4xI", response.data, response.offset)[0]

    def _read_next_block(self, block_address, response):
        self._next_block_address, free = struct.unpack_from(
            "<II", response.data, response.offset)
        if self._next_block_address != 0:
            self._blocks.append(HeapElement(
                block_address, self._next_block_address, free))

    def _read_address(self, x, y, address, size, callback):
        self._send_request(
            ReadMemory(x, y, address, size), callback)
        self._finish()
        self.check_for_error()

    def get_heap(self, x, y, pointer=HEAP_ADDRESS):
        self._read_address(
            x, y, constants.SYSTEM_VARIABLE_BASE_ADDRESS + pointer.offset,
            pointer.data_type.value, self._read_heap_address_response)

        self._read_address(
            x, y, self._heap_address, 8, self._read_heap_pointer)

        while self._next_block_address != 0:
            self._read_address(
                x, y, self._next_block_address, 8,
                functools.partial(
                    self._read_next_block, self._next_block_address)
            )

        return self._blocks
