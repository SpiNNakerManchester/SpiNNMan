import functools
from spinnman.messages.scp.impl.scp_read_memory_request \
    import SCPReadMemoryRequest
from spinnman.processes.abstract_multi_connection_process \
    import AbstractMultiConnectionProcess


class ReadMemoryProcess(AbstractMultiConnectionProcess):
    """ A process for reading memory
    """

    def __init__(self, connections, next_connection_selector=None):
        AbstractMultiConnectionProcess.__init__(
            self, connections, next_connection_selector)
        self._view = None

    def handle_response(self, offset, response):
        self._view[offset:offset + response.length] = response.data[
            response.offset:response.offset + response.length]

    def read_memory(self, x, y, base_address, length):
        data = bytearray(length)
        self._view = memoryview(data)
        n_bytes = length
        offset = 0
        while n_bytes > 0:

            bytes_to_get = n_bytes
            if bytes_to_get > 256:
                bytes_to_get = 256

            response_handler = functools.partial(self.handle_response, offset)
            self._send_request(
                SCPReadMemoryRequest(0, 0, base_address + offset,
                                     bytes_to_get),
                response_handler)

            n_bytes -= bytes_to_get
            offset += bytes_to_get

        self._finish()
        self.check_for_error()
        return data
