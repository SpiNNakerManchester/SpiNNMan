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
from typing import Optional, Sequence


class BMPConnectionData(object):
    """
    Contains the details of a BMP connection.
    """
    __slots__ = [
        "_boards",
        "_ip_address",
        "_port_num"]

    def __init__(self, ip_address: str, boards: Sequence[int],
                 port_num: Optional[int]):
        """

        :param ip_address: The IP address of the BMP.
        :param boards: The boards to be addressed.
        :param port_num: The port number associated with this BMP connection.
        """
        self._ip_address = ip_address
        self._boards = tuple(boards)
        self._port_num = port_num

    @property
    def ip_address(self) -> str:
        """
        The IP address of the BMP.
        """
        return self._ip_address

    @property
    def boards(self) -> Sequence[int]:
        """
        The boards to be addressed.
        """
        return self._boards

    @property
    def port_num(self) -> Optional[int]:
        """
        The port number associated with this BMP connection.
        """
        return self._port_num

    def __str__(self) -> str:
        return f"{self._ip_address}:{self._boards}:{self._port_num}"

    def __repr__(self) -> str:
        return self.__str__()
