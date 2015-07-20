from spinnman.messages.scp.impl.scp_write_link_request \
    import SCPWriteLinkRequest
from spinnman.processes.abstract_multi_connection_process \
    import AbstractMultiConnectionProcess
from spinnman.messages.scp.impl.scp_write_memory_request \
    import SCPWriteMemoryRequest

import functools


class WriteMemoryProcess(AbstractMultiConnectionProcess):
    """ A process for writing memory
    """

    def __init__(self, connections, next_connection_selector=None):
        AbstractMultiConnectionProcess.__init__(
            self, connections, next_connection_selector,
            n_channels=1, intermediate_channel_waits=0)

    def write_memory_from_bytearray(self, x, y, p, base_address, data, offset,
                                    n_bytes):
        self._write_memory_from_bytearray(
            base_address, data, offset, n_bytes,
            functools.partial(SCPWriteMemoryRequest, x=x, y=y, cpu=p))

    def write_link_memory_from_bytearray(self, x, y, p, link, base_address,
                                         data, offset, n_bytes):
        self._write_memory_from_bytearray(
            base_address, data, offset, n_bytes,
            functools.partial(SCPWriteLinkRequest, x=x, y=y, cpu=p, link=link))

    def write_memory_from_reader(self, x, y, p, base_address, data, n_bytes):
        self._write_memory_from_reader(
            base_address, data, n_bytes,
            functools.partial(SCPWriteMemoryRequest, x=x, y=y, cpu=p))

    def write_link_memory_from_reader(self, x, y, p, link, base_address, data,
                                      n_bytes):
        self._write_memory_from_reader(
            base_address, data, n_bytes,
            functools.partial(SCPWriteLinkRequest, x=x, y=y, cpu=p, link=link))

    def _write_memory_from_bytearray(self, base_address, data, offset,
                                     n_bytes, packet_class):
        data_offset = offset
        offset = base_address
        n_bytes_to_write = int(n_bytes)
        n_bytes_written = 0
        while n_bytes_to_write > 0:

            bytes_to_send = n_bytes_to_write
            if bytes_to_send > 256:
                bytes_to_send = 256

            request = packet_class(
                base_address=offset, 
                data=data[data_offset:data_offset + bytes_to_send])
            self._send_request(request)

            n_bytes_to_write -= bytes_to_send
            offset += bytes_to_send
            data_offset += bytes_to_send
            n_bytes_written += bytes_to_send
            if n_bytes_written > 1000000:
                self._finish()
        self._finish()
        self.check_for_error()

    def _write_memory_from_reader(self, base_address, data, n_bytes,
                                  packet_class):
        offset = base_address
        n_bytes_to_write = int(n_bytes)
        n_bytes_written = 0
        while n_bytes_to_write > 0:

            bytes_to_send = n_bytes_to_write
            if bytes_to_send > 256:
                bytes_to_send = 256
            data_array = data.read(bytes_to_send)
            data_length = len(data_array)

            request = packet_class(base_address=offset, data=data_array)
            self._send_request(request)

            n_bytes_to_write -= bytes_to_send
            offset += bytes_to_send
            n_bytes_written += bytes_to_send
            if n_bytes_written > 1000000:
                self._finish()
        self._finish()
        self.check_for_error()
