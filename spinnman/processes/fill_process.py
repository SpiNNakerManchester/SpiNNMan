import struct
from enum import Enum
from spinnman.messages.scp.impl.scp_fill_request import SCPFillRequest
from spinnman.messages.scp.impl import WriteMemory
from spinnman.processes.abstract_multi_connection_process \
    import AbstractMultiConnectionProcess


class FillDataType(Enum):

    WORD = (4, "<I")
    HALF_WORD = (2, "<2H")
    BYTE = (1, "<4B")

    def __new__(cls, value, struct_type, doc=""):
        obj = object.__new__(cls)
        obj._value_ = value
        obj._struct_type = struct_type
        return obj

    def __init__(self, value, struct_type, doc=""):
        self._value_ = value
        self._struct_type = struct_type
        self.__doc__ = doc

    @property
    def struct_type(self):
        return self._struct_type


class FillProcess(AbstractMultiConnectionProcess):
    """ A process for filling memory
    """

    def __init__(self, connection_selector):
        AbstractMultiConnectionProcess.__init__(self, connection_selector)

    def fill_memory(self, x, y, base_address, data, size, data_type):

        # Don't do anything if there is nothing to do!
        if size == 0:
            return

        # Check that the data can fill the requested size
        if size % data_type.value != 0:
            raise Exception(
                "The size of {} bytes to fill is not divisible by the size of"
                " the data of {} bytes".format(size, data_type.value))

        # Work out how many unaligned bytes need to be sent
        extra_bytes = (4 - (base_address % 4)) % 4
        bytes_to_write = size
        address = base_address

        # Get a word of data regardless of the type
        data_to_fill = bytearray(struct.pack(
            "{}".format(data_type.struct_type),
            *([data] * (4 / data_type.value))
        ))

        # Pre bytes is the first part of the data up to the first aligned
        # word
        pre_bytes = struct.pack(
            "<{}B".format(extra_bytes), *(data_to_fill[:extra_bytes]))

        # Post bytes is the last part of the data from the end of the last
        # aligned word
        n_post_bytes = (4 - extra_bytes) % 4
        post_bytes = b""
        if n_post_bytes != 0:
            post_bytes = struct.pack(
                "<{}B".format(n_post_bytes), *(data_to_fill[-n_post_bytes:]))

        # The data to send is the repeated fill data, from the end of the
        # pre-data circling round to the start of the post-data
        data_to_send = struct.unpack("<I", struct.pack("<4B", *([
            data_to_fill[i % 4] for i in range(extra_bytes, extra_bytes + 4)
        ])))[0]

        # Send the pre-data to make the memory aligned (or all the
        # data if the size is correct - note that pre_bytes[:size] will
        # return all of pre_bytes if size >= len(pre_bytes)
        pre_data = pre_bytes[:size]
        if len(pre_data) > 0:
            self._send_request(WriteMemory(
                x, y, base_address, pre_bytes[:size]))
            bytes_to_write -= extra_bytes
            address += extra_bytes

        # Fill as much as possible
        fill_bytes = size
        if extra_bytes != 0:
            fill_bytes -= 4
        if fill_bytes > 0:
            self._send_request(SCPFillRequest(
                x, y, address, data_to_send, fill_bytes))
            bytes_to_write -= fill_bytes
            address += fill_bytes

        # Send the post-data if required
        if bytes_to_write > 0:
            self._send_request(SCPWriteMemoryRequest(
                x, y, address, post_bytes[:bytes_to_write]))

        # Wait for all the packets to be confirmed and then check there
        # are no errors
        self._finish()
        self.check_for_error()
