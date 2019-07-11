# Copyright (c) 2017-2019 The University of Manchester
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import struct
from six import add_metaclass
from spinn_utilities.abstract_base import AbstractBase, abstractmethod

_THREE_WORDS = struct.Struct("<III")


@add_metaclass(AbstractBase)
class AbstractSCPRequest(object):
    """ Represents an Abstract SCP Request
    """
    __slots__ = [
        "_argument_1",
        "_argument_2",
        "_argument_3",
        "_data",
        "_scp_request_header",
        "_sdp_header"]

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
            :py:class:`spinnman.messages.scp.SCPRequestHeader`
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
        # pylint: disable=too-many-arguments
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
            :py:class:`spinnman.messages.scp.SCPRequestHeader`
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
        data += _THREE_WORDS.pack(
            0 if self._argument_1 is None else self._argument_1,
            0 if self._argument_2 is None else self._argument_2,
            0 if self._argument_3 is None else self._argument_3)
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
