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

import re
import struct
from time import localtime, asctime
from spinnman.exceptions import SpinnmanInvalidParameterException

_VERSION_PATTERN = struct.Struct("<BBBBHHI")


class VersionInfo(object):
    """
    Decodes SC&MP/SARK version information as returned by the SVER command.
    """
    __slots__ = [
        "_build_date",
        "_hardware",
        "_name",
        "_physical_cpu_id",
        "_version_number",
        "_version_string",
        "_x", "_y", "_p"]

    def __init__(self, version_data, offset=0):
        """
        :param bytes version_data:
            bytes from an SCP packet containing version information
        :param int offset:
            the offset in the bytes from an SCP packet containing
            version information
        :raise SpinnmanInvalidParameterException:
            If the message does not contain valid version information
        """
        (self._p, self._physical_cpu_id, self._y, self._x, _,
            version_no, self._build_date) = _VERSION_PATTERN.unpack_from(
                memoryview(version_data), offset)

        version_data = version_data[offset + 12:-1].decode("utf-8")

        if version_no < 0xFFFF:
            try:
                self._version_number = (version_no // 100, version_no % 100, 0)
                self._name, self._hardware = version_data.split("/")
                self._version_string = version_data
            except ValueError as exception:
                raise SpinnmanInvalidParameterException(
                    "version_data", version_data,
                    f"Incorrect format: {exception}") from exception
        else:
            name_hardware, _, version = version_data.partition("\0")
            self._version_string = version
            matches = re.match(r"(\d+)\.(\d+)\.(\d+)", version)
            if matches is None:
                raise SpinnmanInvalidParameterException(
                    "version", version, "Cannot be parsed")
            self._version_number = tuple(map(int, matches.group(1, 2, 3)))
            self._name, self._hardware = name_hardware.rstrip("\0").split("/")

    @property
    def name(self):
        """
        The name of the software.

        :rtype: str
        """
        return self._name

    @property
    def version_number(self):
        """
        The version number of the software.

        :rtype: tuple(int, int, int)
        """
        return self._version_number

    @property
    def hardware(self):
        """
        The hardware being run on.

        :rtype: str
        """
        return self._hardware

    @property
    def x(self):
        """
        The X-coordinate of the chip where the information was obtained.

        :rtype: int
        """
        return self._x

    @property
    def y(self):
        """
        The Y-coordinate of the chip where the information was obtained.

        :rtype: int
        """
        return self._y

    @property
    def p(self):
        """
        The processor ID of the processor where the information was obtained.

        :rtype: int
        """
        return self._p

    @property
    def build_date(self):
        """
        The build date of the software, in seconds since 1st January 1970.

        :rtype: int
        """
        return self._build_date

    @property
    def version_string(self):
        """
        The version information as text.

        :rtype: str
        """
        return self._version_string

    def __str__(self):
        return "[Version: {} {} at {}:{}:{}:{} (built {})]".format(
            self._name, self._version_string, self._hardware, self._x, self._y,
            self._p, asctime(localtime(self._build_date)))
