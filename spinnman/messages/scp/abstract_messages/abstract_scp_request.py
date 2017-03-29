from six import add_metaclass
import struct

from spinn_utilities.abstract_base import AbstractBase, abstractmethod


@add_metaclass(AbstractBase)
class AbstractSCPRequest(object):
    """ Represents an Abstract SCP Request
    """

    DEFAULT_DEST_X_COORD = 255
    DEFAULT_DEST_Y_COORD = 255

    def __init__(self, sdp_header, scp_request_header, argument_1=None,
                 argument_2=None, argument_3=None, data=None):
        """

        :param sdp_header: The SDP header of the request
        :type sdp_header:\
                    :py:class:`spinnman.messages.sdp.sdp_header.SDPHeader`
        :param scp_request_header: The SCP header of the request
        :type scp_request_header:\
                    :py:class:`spinnman.messages.scp.scp_request_header.SCPRequestHeader`
        :param argument_1: The first argument, or None if no first argument
        :type argument_1: int
        :param argument_2: The second argument, or None if no second argument
        :type argument_2: int
        :param argument_3: The third argument, or None if no third argument
        :type argument_3: int
        :param data: The optional data, or None if no data
        :type data: bytearray
        :raise None: No known exceptions are raised
        """
        self._sdp_header = sdp_header
        self._scp_request_header = scp_request_header
        self._argument_1 = argument_1
        self._argument_2 = argument_2
        self._argument_3 = argument_3
        self._data = data

    @property
    def sdp_header(self):
        """ The SDP header of the message

        :rtype: :py:class:`spinnman.message.sdp.sdp_header.SDPHeader`
        """
        return self._sdp_header

    @property
    def scp_request_header(self):
        """ The SCP request header of the message

        :rtype:\
                    :py:class:`spinnman.messages.scp.scp_request_header.SCPRequestHeader`
        """
        return self._scp_request_header

    @property
    def argument_1(self):
        """ The first argument, or None if no first argument

        :rtype: int
        """
        return self._argument_1

    @property
    def argument_2(self):
        """ The second argument, or None if no second argument

        :rtype: int
        """
        return self._argument_2

    @property
    def argument_3(self):
        """ The third argument, or None if no third argument

        :rtype: int
        """
        return self._argument_3

    @property
    def data(self):
        """ The data, or None if no data

        :rtype: bytearray
        """
        return self._data

    @property
    def bytestring(self):
        """ The request as a bytestring

        :return: The request as a bytestring
        :rtype: str
        """
        data = (self._sdp_header.bytestring +
                self._scp_request_header.bytestring)
        if self._argument_1 is not None:
            data += struct.pack("<I", self._argument_1)
        else:
            data += struct.pack("<I", 0)
        if self._argument_2 is not None:
            data += struct.pack("<I", self._argument_2)
        else:
            data += struct.pack("<I", 0)
        if self._argument_3 is not None:
            data += struct.pack("<I", self._argument_3)
        else:
            data += struct.pack("<I", 0)
        if self._data is not None:
            data += bytes(self._data)
        return data

    @abstractmethod
    def get_scp_response(self):
        """ Get an SCP response message to be used to process any response\
            received

        :return: An SCP response, or None if no response is required
        :rtype: :py:class:`spinnman.messages.scp_response.SCPResponse`
        :raise None: No known exceptions are raised
        """
        pass
