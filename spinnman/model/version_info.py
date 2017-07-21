from spinnman.exceptions import SpinnmanInvalidParameterException
from time import localtime, asctime
import struct
import re


class VersionInfo(object):
    """ Decodes SC&MP/SARK version information as returned by the SVER command
    """

    def __init__(self, version_data, offset=0):
        """
        :param version_data: bytes from an SCP packet containing version\
                    information
        :param offset: the offset in the bytes from an SCP packet containing
                       version information
        :type version_data: bytearray
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If the\
                    message does not contain valid version information
        """
        (self._p, self._physical_cpu_id, self._y, self._x, _,
            version_no, self._build_date) = struct.unpack_from(
                "<BBBBHHI", buffer(version_data), offset)

        version_data = version_data[offset + 12:-1].decode("utf-8")

        if version_no < 0xFFFF:
            try:
                self._version_number = (version_no // 100, version_no % 100, 0)
                self._name, self._hardware = version_data.split("/")
                self._version_string = version_data
            except ValueError as exception:
                raise SpinnmanInvalidParameterException(
                    "version_data", version_data,
                    "Incorrect format: {}".format(exception))
        else:
            name_hardware, _, version = version_data.partition("\0")
            self._version_string = version
            matches = re.match("(\d+)\.(\d+)\.(\d+)", version)
            if matches is None:
                raise SpinnmanInvalidParameterException(
                    "version", version, "Cannot be parsed")
            self._version_number = tuple(map(int, matches.group(1, 2, 3)))
            self._name, self._hardware = name_hardware.rstrip("\0").split("/")

    @property
    def name(self):
        """ The name of the software

        :return: The name
        :rtype: str
        """
        return self._name

    @property
    def version_number(self):
        """ The version number of the software

        :return: The version
        :rtype: float
        """
        return self._version_number

    @property
    def hardware(self):
        """ The hardware being run on

        :return: The hardware
        :rtype: str
        """
        return self._hardware

    @property
    def x(self):
        """ The x-coordinate of the chip where the information was obtained

        :return: the x-coordinate
        :rtype: int
        """
        return self._x

    @property
    def y(self):
        """ The y-coordinate of the chip where the information was obtained

        :return: The y-coordinate
        :rtype: int
        """
        return self._y

    @property
    def p(self):
        """ The processor id of the processor where the information was\
                    obtained

        :return: the processor id
        :rtype: int
        """
        return self._p

    @property
    def build_date(self):
        """ The build date of the software

        :return: The number of seconds since 1st January 1970
        :rtype: long
        """
        return self._build_date

    @property
    def version_string(self):
        """ The version information as text

        :return: The version information
        :rtype: str
        """
        return self._version_string

    def __str__(self):
        return "[Version: {} {} at {}:{}:{}:{} (built {})]".format(
            self._name, self._version_string, self._hardware, self._x, self._y,
            self._p, asctime(localtime(self._build_date)))
