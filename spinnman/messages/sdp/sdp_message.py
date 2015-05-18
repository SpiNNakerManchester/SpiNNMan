from spinnman.messages.sdp.sdp_header import SDPHeader
from spinnman.messages.sdp import sdp_header


class SDPMessage(object):
    """ Wraps up an SDP message with a header and optional data.
    """

    def __init__(self, sdp_header=None, data=None):
        """
        :param sdp_header: The header of the message
        :type sdp_header:\
                    :py:class:`spinnman.messages.sdp.sdp_header.SDPHeader`
        :param data: The data of the SDP packet, or None if no data
        :type data: bytearray
        :raise None: No known exceptions are thrown
        """

        self._sdp_header = sdp_header
        self._data = data

    @property
    def bytestring(self):
        """ The bytestring of the message

        :return: The bytestring of the message
        :rtype: bytestring
        """
        if self._data is not None:
            return self._sdp_header.bytestring + self._data
        return self._sdp_header.bytestring

    def read_bytestring(self, data, offset):
        if self._sdp_header is None:
            self._sdp_header = SDPHeader()
        self._sdp_header.read_bytestring(data, offset)
        self._data = data[offset + sdp_header.N_BYTES:]

    @property
    def sdp_header(self):
        """ The header of the packet

        :return: An SDP header
        :rtype: :py:class:`spinnman.messages.sdp.sdp_header.SDPHeader`
        """
        return self._sdp_header

    @property
    def data(self):
        """ The data in the packet

        :return: The data
        :rtype: bytearray
        """
        return self._data
