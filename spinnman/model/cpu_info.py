from spinnman.model.cpu_state import CPUState
from spinnman.model.run_time_error import RunTimeError
from spinnman.model.mailbox_command import MailboxCommand
from spinnman.exceptions import SpinnmanInvalidParameterException
from spinnman._utils import _get_int_from_little_endian_bytearray
from spinnman._utils import _get_short_from_little_endian_bytearray
from spinnman import constants

def _get_int_from_bytearray(array, offset):
    """ Wrapper function in case the endianness changes
    """
    return _get_int_from_little_endian_bytearray(array, offset)


def _get_short_from_bytearray(array, offset):
    """ Wrapper function in case the endianness changes
    """
    return _get_short_from_little_endian_bytearray(array, offset)

CPU_INFO_BYTES = 128
CPU_USER_0_START_ADDRESS = 112

class CPUInfo(object):
    """ Represents information about the state of a CPU
    """

    def __init__(self, x, y, p, cpu_data):
        """
        :param x: The x-coordinate of a chip
        :type x: int
        :param y: The y-coordinate of a chip
        :type y: int
        :param p: The id of a core on the chip
        :type p: int
        :param cpu_data: An array of bytes received from SDRAM on the board
        :type cpu_data: bytearray
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If the\
                    array does not contain a cpu data structure
        """
        if len(cpu_data) != constants.CPU_INFO_BYTES:
            raise SpinnmanInvalidParameterException(
                    "len(cpu_data)", str(len(cpu_data)),
                    "Must be 128 bytes of data")

        self._x = x
        self._y = y
        self._p = p

        self._registers = [_get_int_from_bytearray(cpu_data, i)
                           for i in range(0, 32, 4)]
        self._processor_state_register = _get_int_from_bytearray(cpu_data, 32)
        self._stack_pointer = _get_int_from_bytearray(cpu_data, 36)
        self._link_register = _get_int_from_bytearray(cpu_data, 40)
        self._run_time_error = RunTimeError(cpu_data[44])
        self._state = CPUState(cpu_data[46])
        self._application_id = cpu_data[47]
        self._application_mailbox_data_address =\
                    _get_int_from_bytearray(cpu_data, 48)
        self._monitor_mailbox_data_address =\
                    _get_int_from_bytearray(cpu_data, 52)
        self._application_mailbox_command = MailboxCommand(cpu_data[56])
        self._monitor_mailbox_command = MailboxCommand(cpu_data[57])
        self._software_error_count = _get_short_from_bytearray(cpu_data, 58)
        self._software_source_filename_address =\
                    _get_int_from_bytearray(cpu_data, 60)
        self._software_source_line_number =\
                    _get_int_from_bytearray(cpu_data, 64)
        self._time = _get_int_from_bytearray(cpu_data, 68)
        self._application_name = cpu_data[72:88].decode("ascii")
        self._iobuf_address = _get_int_from_bytearray(cpu_data, 88)
        self._user = [_get_int_from_bytearray(cpu_data, i)
                      for i in range(constants.CPU_USER_0_START_ADDRESS, 128, 4)]

    @property
    def x(self):
        """ The x-coordinate of the chip containing the core

        :return: The x-coordinate of the chip
        :rtype: int
        """
        return self._x

    @property
    def y(self):
        """ The y-coordinate of the chip containing the core

        :return: The y-coordinate of the chip
        :rtype: int
        """
        return self._y

    @property
    def p(self):
        """ The id of the core on the chip

        :return: The id of the core
        :rtype: int
        """
        return self._p

    @property
    def state(self):
        """ The current state of the core

        :return: The state of the core
        :rtype: :py:class:`spinnman.model.cpu_state.CPUState`
        """
        return self._state

    @property
    def application_name(self):
        """ The name of the application running on the core

        :return: The name of the application
        :rtype: str
        """
        return self._application_name

    @property
    def application_id(self):
        """ The id of the application running on the core

        :return: The id of the application
        :rtype: int
        """
        return self._application_id

    @property
    def time(self):
        """ The time at which the application started

        :return: The time in seconds since 00:00:00 on the 1st January 1970
        :rtype: long
        """
        return self._time

    @property
    def run_time_error(self):
        """ The reason for a run time error

        :return: The run time error
        :rtype: :py:class:`spinnman.model.run_time_error.RunTimeError`
        """
        return self._run_time_error

    @property
    def application_mailbox_command(self):
        """ The command currently in the mailbox being sent from the monitor\
            processor to the application

        :return: The command
        :rtype: :py:class:`spinnman.model.mailbox_command.MailboxCommand`
        """
        return self._application_mailbox_command

    @property
    def application_mailbox_data_address(self):
        """ The address of the data in SDRAM for the application mailbox

        :return: The address of the data
        :rtype: int
        """
        return self._application_mailbox_data_address

    @property
    def monitor_mailbox_command(self):
        """ The command currently in the mailbox being sent from the\
            application to the monitor processor

        :return: The command
        :rtype: :py:class:`spinnman.model.mailbox_command.MailboxCommand`
        """
        return self._monitor_mailbox_command

    @property
    def monitor_mailbox_data_address(self):
        """ The address of the data in SDRAM of the monitor mailbox

        :return: The address of the data
        :rtype: int
        """
        return self._monitor_mailbox_data_address

    @property
    def software_error_count(self):
        """ The number of software errors counted

        :return: The number of software errors
        :rtype: int
        """
        return self._software_error_count

    @property
    def software_source_filename_address(self):
        """ The address of the filename of the software source

        :return: The filename
        :rtype: str
        """
        return self._software_source_filename_address

    @property
    def software_source_line_number(self):
        """ The line number of the software source

        :return: The line number
        :rtype: int
        """
        return self._software_source_line_number

    @property
    def processor_state_register(self):
        """ The value in the processor state register (psr)

        :return: The psr value
        :rtype: int
        """
        return self._processor_state_register

    @property
    def stack_pointer(self):
        """ The current stack pointer value (sp)

        :return: The sp value
        :rtype: int
        """
        return self._stack_pointer

    @property
    def link_register(self):
        """ The current link register value (lr)

        :return: The lr value
        :rtype: int
        """
        return self._link_register

    @property
    def registers(self):
        """ The current register values (r0 - r7)

        :return: An array of 8 values, one for each register
        :rtype: array of int
        """
        return self._registers

    @property
    def user(self):
        """ The current user values (user0 - user3)

        :return: An array of 4 values, one for each user value
        :rtype: array of int
        """
        return self._user

    @property
    def iobuf_address(self):
        """ The address of the IOBUF buffer in SDRAM

        :return: The address
        :rtype: int
        """
        return self._iobuf_address

    def __str__(self):
        return "{}:{}:{:02n} {:18} {:16s} {:3n}".format(
            self.x, self.y, self.p, self._state.name, self._application_name,
            self._application_id)
