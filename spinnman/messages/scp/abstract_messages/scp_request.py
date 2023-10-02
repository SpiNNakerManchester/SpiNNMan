# Copyright (c) 2014 The University of Manchester
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import struct
from spinn_utilities.abstract_base import AbstractBase, abstractmethod

_THREE_WORDS = struct.Struct("<III")


class AbstractSCPRequest(object, metaclass=AbstractBase):
    """
    Represents an Abstract SCP Request.
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
        :param SDPHeader sdp_header: The SDP header of the request
        :param SCPRequestHeader scp_request_header:
            The SCP header of the request
        :param int argument_1:
            The first argument, or `None` if no first argument
        :param int argument_2:
            The second argument, or `None` if no second argument
        :param int argument_3:
            The third argument, or `None` if no third argument
        :param data: The optional data, or `None` if no data
        :type data: bytearray or bytes or None
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
        """
        The SDP header of the message.

        :rtype: SDPHeader
        """
        return self._sdp_header

    @property
    def scp_request_header(self):
        """
        The SCP request header of the message.

        :rtype: SCPRequestHeader
        """
        return self._scp_request_header

    @property
    def argument_1(self):
        """
        The first argument, or `None` if no first argument.

        :rtype: int
        """
        return self._argument_1

    @property
    def argument_2(self):
        """
        The second argument, or `None` if no second argument.

        :rtype: int
        """
        return self._argument_2

    @property
    def argument_3(self):
        """
        The third argument, or `None` if no third argument.

        :rtype: int
        """
        return self._argument_3

    @property
    def data(self):
        """
        The data, or `None` if no data.

        :rtype: bytearray
        """
        return self._data

    @property
    def bytestring(self):
        """
        The request as a byte-string.

        :rtype: bytes
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

    def __repr__(self):
        # Default is to return just the command, but can be overridden
        return str(self._scp_request_header.command)

    def __str__(self):
        return self.__repr__()

    @abstractmethod
    def get_scp_response(self):
        """
        Get an SCP response message to be used to process any response
        received.

        :return: An SCP response, or `None` if no response is required
        :rtype: AbstractSCPResponse
        """
