from .eieio_command_message import EIEIOCommandMessage
from .eieio_command_header import EIEIOCommandHeader
from spinnman.constants import EIEIO_COMMAND_IDS
import struct


class SpinnakerRequestBuffers(EIEIOCommandMessage):
    """ Message used in the context of the buffering input mechanism which is\
        sent by the SpiNNaker system to the host computer to ask for more data\
        to inject during the simulation
    """
    def __init__(self, x, y, p, region_id, sequence_no, space_available):
        EIEIOCommandMessage.__init__(
            self, EIEIOCommandHeader(
                EIEIO_COMMAND_IDS.SPINNAKER_REQUEST_BUFFERS.value))
        self._x = x
        self._y = y
        self._p = p
        self._region_id = region_id
        self._sequence_no = sequence_no
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
        return 12

    @staticmethod
    def from_bytestring(command_header, data, offset):
        y, x, processor, region_id, sequence_no, space = struct.unpack_from(
            "<BBBxBBI", data, offset)
        p = (processor >> 3) & 0x1F
        return SpinnakerRequestBuffers(x, y, p, region_id & 0xF, sequence_no,
                                       space)

    @property
    def bytestring(self):
        return (super(SpinnakerRequestBuffers, self).bytestring + struct.pack(
            "<BBBxBBI", self._y, self._x, self._p << 3, self._region_id,
            self._sequence_no, self._space_available))
