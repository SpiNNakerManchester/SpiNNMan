from spinnman.processes.abstract_multi_connection_process \
    import AbstractMultiConnectionProcess
from spinnman.messages.scp.impl.scp_write_memory_request \
    import SCPWriteMemoryRequest


class WriteMemoryProcess(AbstractMultiConnectionProcess):
    """ A process for writing memory
    """

    def __init__(self, connections, next_connection_selector=None):
        AbstractMultiConnectionProcess.__init__(
            self, connections, next_connection_selector)

    def write_memory_from_bytearray(self, x, y, base_address, data, offset,
                                    n_bytes):
        data_offset = offset
        offset = base_address
        while n_bytes > 0:

            bytes_to_send = int(n_bytes)
            if bytes_to_send > 256:
                bytes_to_send = 256

            self._send_request(
                SCPWriteMemoryRequest(x, y, offset, data, data_offset,
                                      bytes_to_send))

            n_bytes -= bytes_to_send
            offset += bytes_to_send
            data_offset += bytes_to_send
        self._finish()
        self.check_for_error()

    def write_memory_from_reader(self, x, y, base_address, data, n_bytes):
        offset = base_address
        while n_bytes > 0:

            bytes_to_send = int(n_bytes)
            if bytes_to_send > 256:
                bytes_to_send = 256
            data_array = data.read(bytes_to_send)

            self._send_request(
                SCPWriteMemoryRequest(x, y, offset, data_array, 0,
                                      len(data_array)))

            n_bytes -= bytes_to_send
            offset += bytes_to_send
        self._finish()
        self.check_for_error()
