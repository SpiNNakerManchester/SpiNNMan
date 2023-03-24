# Copyright (c) 2015 The University of Manchester
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


class BMPConnectionData(object):
    """
    Contains the details of a BMP connection.
    """
    __slots__ = [
        "_boards",
        "_cabinet",
        "_frame",
        "_ip_address",
        "_port_num"]

    def __init__(self, cabinet, frame, ip_address, boards, port_num):
        # pylint: disable=too-many-arguments
        self._cabinet = cabinet
        self._frame = frame
        self._ip_address = ip_address
        self._boards = boards
        self._port_num = port_num

    @property
    def cabinet(self):
        """
        The cabinet number.

        :rtype: int
        """
        return self._cabinet

    @property
    def frame(self):
        """
        The frame number.

        :rtype: int
        """
        return self._frame

    @property
    def ip_address(self):
        """
        The IP address of the BMP.

        :rtype: str
        """
        return self._ip_address

    @property
    def boards(self):
        """
        The boards to be addressed.

        :rtype: iterable(int)
        """
        return self._boards

    @property
    def port_num(self):
        """
        The port number associated with this BMP connection.

        :return: The port number
        """
        return self._port_num

    def __str__(self):
        return (f"{self._cabinet}:{self._frame}:{self._ip_address}:"
                f"{self._boards}:{self._port_num}")

    def __repr__(self):
        return self.__str__()
