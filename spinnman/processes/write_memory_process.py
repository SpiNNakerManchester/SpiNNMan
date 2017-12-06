from spinnman.messages.scp.impl import WriteLink, WriteMemory
from .abstract_multi_connection_process import AbstractMultiConnectionProcess
from spinnman.constants import UDP_MESSAGE_MAX_SIZE

import functools


class WriteMemoryProcess(AbstractMultiConnectionProcess):
    """ A process for writing memory
    """
    # pylint: disable=too-many-arguments

    def __init__(self, connection_selector):
        AbstractMultiConnectionProcess.__init__(self, connection_selector)

    def write_memory_from_bytearray(
            self, processor_address, base_address, data, offset, n_bytes):
        """ Writes memory onto a spinnaker chip from a bytearray

        :param processor_address: the (x, y, p) coords of the chip in question
        :param base_address: the address in sdram to start writing
        :param data: the data to write
        :param offset: where in the data to start writing from
        :param n_bytes: how much data to write
        :rtype: None
        """
        (x, y, p) = processor_address
        self._write_memory_from_bytearray(
            base_address, data, offset, n_bytes,
            functools.partial(WriteMemory, x=x, y=y, cpu=p))

    def write_link_memory_from_bytearray(
            self, processor_address, link, base_address, data, offset,
            n_bytes):
        (x, y, p) = processor_address
        self._write_memory_from_bytearray(
            base_address, data, offset, n_bytes,
            functools.partial(WriteLink, x=x, y=y, cpu=p, link=link))

    def write_memory_from_reader(
            self, processor_address, base_address, reader, n_bytes):
        """ Writes memory onto a spinnaker chip from a reader

        :param processor_address: the (x, y, p) coords of the chip in question
        :param base_address: the address in sdram to start writing
        :param reader: the reader containing the data to write
        :param n_bytes: how much data to write
        :rtype: None
        """
        (x, y, p) = processor_address
        self._write_memory_from_reader(
            base_address, reader, n_bytes,
            functools.partial(WriteMemory, x=x, y=y, cpu=p))

    def write_link_memory_from_reader(
            self, processor_address, link, base_address, reader, n_bytes):
        (x, y, p) = processor_address
        self._write_memory_from_reader(
            base_address, reader, n_bytes,
            functools.partial(WriteLink, x=x, y=y, cpu=p, link=link))

    def _write_memory_from_bytearray(self, base_address, data, data_offset,
                                     n_bytes, packet_class):
        offset = 0
        n_bytes_to_write = int(n_bytes)
        while n_bytes_to_write > 0:
            bytes_to_send = min((n_bytes_to_write, UDP_MESSAGE_MAX_SIZE))
            data_array = data[data_offset:data_offset + bytes_to_send]

            self._send_request(packet_class(
                base_address=base_address + offset,
                data=data_array))

            n_bytes_to_write -= bytes_to_send
            offset += bytes_to_send
            data_offset += bytes_to_send
        self._finish()
        self.check_for_error()

    def _write_memory_from_reader(self, base_address, reader, n_bytes,
                                  packet_class):
        offset = 0
        n_bytes_to_write = int(n_bytes)
        while n_bytes_to_write > 0:
            bytes_to_send = min((n_bytes_to_write, UDP_MESSAGE_MAX_SIZE))
            data_array = reader.read(bytes_to_send)
            bytes_to_send = len(data_array)

            self._send_request(packet_class(
                base_address=base_address + offset,
                data=data_array))

            n_bytes_to_write -= bytes_to_send
            offset += bytes_to_send
        self._finish()
        self.check_for_error()
