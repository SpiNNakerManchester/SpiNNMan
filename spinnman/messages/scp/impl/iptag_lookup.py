from spinn_utilities.overrides import overrides
from spinnman.messages.scp import SCPRequestHeader
from spinnman.messages.scp.abstract_messages import (
    AbstractSCPRequest, AbstractSCPResponse)
from spinnman.messages.scp.enums import SCPCommand, SCPResult
from spinnman.messages.sdp import SDPFlag, SDPHeader
from spinnman.exceptions import SpinnmanUnexpectedResponseCodeException

import struct


_IPTAG_LKP = 5

_IPTAG_FORMAT = struct.Struct("<I4s")


class IPTagLookup(AbstractSCPRequest):
    """ An SCP Request to lookup the sender port and IP address
    """
    __slots__ = []

    def __init__(self, x, y, flag=SDPFlag.REPLY_EXPECTED):
        """
        :param x: The x-coordinate of a chip, between 0 and 255
        :type x: int
        :param y: The y-coordinate of a chip, between 0 and 255
        :type y: int
        :param flag: The flag to use
        """
        super(IPTagLookup, self).__init__(
            SDPHeader(
                flags=flag, destination_port=0,
                destination_cpu=0, destination_chip_x=x,
                destination_chip_y=y),
            SCPRequestHeader(command=SCPCommand.CMD_IPTAG),
            argument_1=(_IPTAG_LKP << 16))

    @overrides(AbstractSCPRequest.get_scp_response)
    def get_scp_response(self):
        return _SCPIPTagLookupResponse()


class _SCPIPTagLookupResponse(AbstractSCPResponse):
    """ An SCP response to a request for the hostname and port
    """
    __slots__ = [
        "_ip_address",
        "_port"]

    def __init__(self):
        """
        """
        super(_SCPIPTagLookupResponse, self).__init__()
        self._ip_address = None
        self._port = None

    @overrides(AbstractSCPResponse.read_data_bytestring)
    def read_data_bytestring(self, data, offset):
        result = self.scp_response_header.result
        if result != SCPResult.RC_OK:
            raise SpinnmanUnexpectedResponseCodeException(
                "IP Tag Lookup", "CMD_IPTAG", result.name)
        (self._port, ip_address) = _IPTAG_FORMAT.unpack_from(data, offset)
        self._ip_address = bytearray(ip_address)

    @property
    def ip_address(self):
        """ The IP address of the tag, as a bytearray of 4 bytes

        :rtype: bytearray
        """
        return self._ip_address

    @property
    def port(self):
        """ The port of the tag

        :rtype: int
        """
        return self._port
