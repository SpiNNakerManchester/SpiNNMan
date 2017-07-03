from spinnman.messages.scp.impl \
    import WriteLink, WriteMemory
from .abstract_multi_connection_process import AbstractMultiConnectionProcess
from spinnman.constants import UDP_MESSAGE_MAX_SIZE

import functools


class WriteMemoryProcess(AbstractMultiConnectionProcess):
    """ A process for writing memory
    """

    def __init__(self, connection_selector):
        AbstractMultiConnectionProcess.__init__(
            self, connection_selector,
            n_channels=1, intermediate_channel_waits=0)

    def write_memory_from_bytearray(
            self, x, y, p, base_address, data, offset, n_bytes):
        """
        writes memory onto a spinnaker chip from a bytearray

        :param x: the x coord of the chip in question
        :param y: the y coord of the chip in question
        :param p: the p coord of the chip in question
        :param base_address: the address in sdram to start writing
        :param data: the data to write
        :param offset: where in the data to start writing from
        :param n_bytes: how much data to write
        :rtype: None
        """
        self._write_memory_from_bytearray(
            base_address, data, offset, n_bytes,
            functools.partial(WriteMemory, x=x, y=y, cpu=p))

    def write_link_memory_from_bytearray(self, x, y, p, link, base_address,
                                         data, offset, n_bytes):
        self._write_memory_from_bytearray(
            base_address, data, offset, n_bytes,
            functools.partial(WriteLink, x=x, y=y, cpu=p, link=link))

    def write_memory_from_reader(self, x, y, p, base_address, data, n_bytes):
        self._write_memory_from_reader(
            base_address, data, n_bytes,
            functools.partial(WriteMemory, x=x, y=y, cpu=p))

    def write_link_memory_from_reader(self, x, y, p, link, base_address, data,
                                      n_bytes):
        self._write_memory_from_reader(
            base_address, data, n_bytes,
            functools.partial(WriteLink, x=x, y=y, cpu=p, link=link))

    def _write_memory_from_bytearray(self, base_address, data, offset,
                                     n_bytes, packet_class):
        data_offset = offset
        offset = base_address
        n_bytes_to_write = int(n_bytes)
        while n_bytes_to_write > 0:
            bytes_to_send = min((n_bytes_to_write, UDP_MESSAGE_MAX_SIZE))
            request = packet_class(
                base_address=offset,
                data=data[data_offset:data_offset + bytes_to_send])
            self._send_request(request)
            n_bytes_to_write -= bytes_to_send
            offset += bytes_to_send
            data_offset += bytes_to_send
        self._finish()
        self.check_for_error()

    def _write_memory_from_reader(self, base_address, data, n_bytes,
                                  packet_class):
        offset = base_address
        n_bytes_to_write = int(n_bytes)
        while n_bytes_to_write > 0:

            bytes_to_send = n_bytes_to_write
            if bytes_to_send > UDP_MESSAGE_MAX_SIZE:
                bytes_to_send = UDP_MESSAGE_MAX_SIZE
            data_array = data.read(bytes_to_send)
            data_length = len(data_array)

            request = packet_class(base_address=offset, data=data_array)
            self._send_request(request)

            n_bytes_to_write -= data_length
            offset += data_length
        self._finish()
        self.check_for_error()
