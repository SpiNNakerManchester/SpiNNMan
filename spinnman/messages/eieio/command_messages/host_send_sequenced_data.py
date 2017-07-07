from .eieio_command_message import EIEIOCommandMessage
from .eieio_command_header import EIEIOCommandHeader
from spinnman.constants import EIEIO_COMMAND_IDS
from spinnman.messages.eieio.create_eieio_data import read_eieio_data_message
import struct


class HostSendSequencedData(EIEIOCommandMessage):
    """ Packet sent from the host to the SpiNNaker system in the context of\
        buffering input mechanism to identify packet which needs to be stored\
        in memory for future use
    """
    def __init__(self, region_id, sequence_no, eieio_data_message):
        EIEIOCommandMessage.__init__(
            self, EIEIOCommandHeader(
                EIEIO_COMMAND_IDS.HOST_SEND_SEQUENCED_DATA.value))
        self._region_id = region_id
        self._sequence_no = sequence_no
        self._eieio_data_message = eieio_data_message

    @property
    def region_id(self):
        return self._region_id

    @property
    def sequence_no(self):
        return self._sequence_no

    @property
    def eieio_data_message(self):
        return self._eieio_data_message

    @staticmethod
    def get_min_packet_length():
        return 4

    @staticmethod
    def from_bytestring(command_header, data, offset):
        region_id, sequence_no = struct.unpack_from("<BB", data, offset)
        eieio_data_message = read_eieio_data_message(data, offset)
        return HostSendSequencedData(region_id, sequence_no,
                                     eieio_data_message)

    @property
    def bytestring(self):
        return (super(HostSendSequencedData, self).bytestring + struct.pack(
            "<BB", self._region_id, self._sequence_no) +
            self._eieio_data_message.bytestring)
