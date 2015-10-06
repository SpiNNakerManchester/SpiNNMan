from spinnman.messages.eieio.command_messages.eieio_command_message\
    import EIEIOCommandMessage
from spinnman.messages.eieio.command_messages.eieio_command_header\
    import EIEIOCommandHeader
from spinnman import constants
import struct


class SpinnakerRequestReadData(EIEIOCommandMessage):

    def __init__(self, x, y, p, region_id, sequence_no, start_address,
                 space_available):
        EIEIOCommandMessage.__init__(
            self, EIEIOCommandHeader(
                constants.EIEIO_COMMAND_IDS.SPINNAKER_REQUEST_READ_DATA.value))
        self._x = x
        self._y = y
        self._p = p
        self._region_id = region_id
        self._sequence_no = sequence_no
        self._start_address = start_address
        self._space_available = space_available

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def p(self):
        return self._p

    @property
    def region_id(self):
        return self._region_id

    @property
    def sequence_no(self):
        return self._sequence_no

    @property
    def space_available(self):
        return self._space_available

    @staticmethod
    def get_min_packet_length():
        return 16

    @staticmethod
    def from_bytestring(command_header, data, offset):
        (y, x, processor, region_id, sequence_no, start_address,
            space_available) = struct.unpack_from("<BBBxBBII", data, offset)
        p = (processor >> 3) & 0x1F
        return SpinnakerRequestReadData(x, y, p, region_id & 0xF, sequence_no,
                                        start_address, space_available)

    @property
    def bytestring(self):
        return (super(SpinnakerRequestReadData, self).bytestring + struct.pack(
            "<BBBxBBI", self._y, self._x, self._p << 3, self._region_id,
            self._sequence_no, self._start_address, self._space_available))
