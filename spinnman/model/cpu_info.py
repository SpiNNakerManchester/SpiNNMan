import struct

from spinnman.model.enums import CPUState, RunTimeError, MailboxCommand

CPU_INFO_BYTES = 128
CPU_USER_0_START_ADDRESS = 112


class CPUInfo(object):
    """ Represents information about the state of a CPU
    """

    def __init__(self, x, y, p, cpu_data, offset):
        """
        :param x: The x-coordinate of a chip
        :type x: int
        :param y: The y-coordinate of a chip
        :type y: int
        :param p: The id of a core on the chip
        :type p: int
        :param cpu_data: A bytestring received from SDRAM on the board
        :type cpu_data: str
        """
        self._x = x
        self._y = y
        self._p = p

        (registers,                                                  # 32s 0
         self._processor_state_register, self._stack_pointer,
         self._link_register,                                        # 3I  32
         run_time_error, self._physical_cpu_id,                      # 2B  44
         state, self._application_id,                                # 2B  46
         self._application_mailbox_data_address,
         self._monitor_mailbox_data_address,                         # 2I  48
         application_mailbox_command, monitor_mailbox_command,       # 2B  56
         self._software_error_count,                                 # H   58
         self._software_source_filename_address,
         self._software_source_line_number, self._time,              # 3I  60
         self._application_name,                                     # 16s 72
         self._iobuf_address, self._software_version,                # 2I  88
         # skipped                                                   # 16x 96
         user0, user1, user2, user3                                  # 4I  112
         ) = struct.unpack_from(
             "< 32s 3I 2B 2B 2I 2B H 3I 16s 2I 16x 4I", cpu_data, offset)

        index = self._application_name.find('\0')
        if index != -1:
            self._application_name = self._application_name[0:index]

        self._registers = struct.unpack_from("<IIIIIIII", registers)
        self._run_time_error = RunTimeError(run_time_error)
        self._state = CPUState(state)

        self._application_mailbox_command = MailboxCommand(
            application_mailbox_command)
        self._monitor_mailbox_command = MailboxCommand(
            monitor_mailbox_command)
        self._user = [user0, user1, user2, user3]

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
        :rtype: :py:class:`spinnman.model.enums.cpu_state.CPUState`
        """
        return self._state

    @property
    def physical_cpu_id(self):
        """ The physical id of this processor

        :return: The physical id of the processor
        :rtype: int
        """
        return self._physical_cpu_id

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
        :rtype: :py:class:`spinnman.model.enums.run_time_error.RunTimeError`
        """
        return self._run_time_error

    @property
    def application_mailbox_command(self):
        """ The command currently in the mailbox being sent from the monitor\
            processor to the application

        :return: The command
        :rtype: :py:class:`spinnman.model.enums.mailbox_command.MailboxCommand`
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
        """ The value in the processor state register (PSR)

        :return: The PSR value
        :rtype: int
        """
        return self._processor_state_register

    @property
    def stack_pointer(self):
        """ The current stack pointer value (SP)

        :return: The SP value
        :rtype: int
        """
        return self._stack_pointer

    @property
    def link_register(self):
        """ The current link register value (LR)

        :return: The LR value
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

    @property
    def software_version(self):
        """ The software version

        :return: The software version
        :rtype: int
        """
        return self._software_version

    def __str__(self):
        return "{}:{}:{:02n} {:18} {:16s} {:3n}".format(
            self.x, self.y, self.p, self._state.name, self._application_name,
            self._application_id)
