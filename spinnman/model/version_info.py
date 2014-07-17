from spinnman.exceptions import SpinnmanInvalidParameterException
from spinnman._utils import _get_int_from_little_endian_bytearray
from spinnman._utils import _get_short_from_little_endian_bytearray
from time import localtime
from time import asctime


def _get_int_from_bytearray(array, offset):
    """ Wrapper function in case the endianness changes
    """
    return _get_int_from_little_endian_bytearray(array, offset)


def _get_short_from_bytearray(array, offset):
    """ Wrapper function in case the endianness changes
    """
    return _get_short_from_little_endian_bytearray(array, offset)


class VersionInfo(object):
    """ Decodes SC&MP/SARK version information as returned by the SVER command
    """

    def __init__(self, version_data):
        """
        :param version_data: bytes from an SCP packet containing version\
                    information
        :type version_data: bytearray
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If the\
                    message does not contain valid version information
        """
        if len(version_data) < 13:
            raise SpinnmanInvalidParameterException(
                    "len(version_data)", len(version_data),
                    "The length of the version data is too short")

        self._p = version_data[0]
        self._y = version_data[2]
        self._x = version_data[3]
        self._version_number = (_get_short_from_bytearray(version_data, 6)
                / 100.0)
        self._build_date = _get_int_from_bytearray(version_data, 8)

        self._version_string = version_data[12:-1].decode("ascii")
        try:
            self._name, self._hardware = self._version_string.split("/")
        except ValueError as exception:
            raise SpinnmanInvalidParameterException(
                    "version_string", self._version_string,
                    "Incorrect format: {}".format(exception))

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
        return "[Version: {} {} at {}:{}:{}:{} (built {})]".format(self._name,
                self._version_number, self._hardware, self._x, self._y,
                self._p, asctime(localtime(self._build_date)))
