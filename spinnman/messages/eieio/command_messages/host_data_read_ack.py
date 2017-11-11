from .eieio_command_message import EIEIOCommandMessage
from .eieio_command_header import EIEIOCommandHeader
from spinnman.constants import EIEIO_COMMAND_IDS
import struct

_PATTERN_B = struct.Struct("<B")


class HostDataReadAck(EIEIOCommandMessage):
    """ Packet sent by the host computer to the SpiNNaker system in the\
        context of the buffering output technique to signal that the host has\
        received a request to read data
    """
    def __init__(self, sequence_no):
        cmd_header = EIEIOCommandHeader(EIEIO_COMMAND_IDS.HOST_DATA_READ.value)
        EIEIOCommandMessage.__init__(self, cmd_header)
        self._sequence_no = sequence_no

    @property
    def sequence_no(self):
        return self._sequence_no

    @staticmethod
    def from_bytestring(command_header, data, offset):  # @UnusedVariable
        sequence_no = _PATTERN_B.unpack_from(data, offset)[0]

        return HostDataReadAck(sequence_no)

    @property
    def bytestring(self):
        byte_string = super(HostDataReadAck, self).bytestring
        byte_string += _PATTERN_B.pack(self.sequence_no)
        return byte_string
