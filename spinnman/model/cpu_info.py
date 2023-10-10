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
from typing import Sequence, Tuple
from typing_extensions import TypeAlias
from spinnman.model.enums import CPUState, RunTimeError, MailboxCommand

#: Size of `vcpu_t` in SARK.
CPU_INFO_BYTES = 128
CPU_USER_0_START_ADDRESS = 112
#: Offset into data of byte of processor state field.
STATE_FIELD_OFFSET = 48

#: Corresponds to vcpu_t in sark.h
_VCPU_PATTERN = struct.Struct("< 32s 3I 2B 2B 2I 2B H 3I 16s 2I 16x 4I")
_vcpu_t: TypeAlias = Tuple[
    bytes,             # 32s - r0-r7
    int, int, int,     # 3I  - psr, sp, lr
    int, int,          # 2B  - RT error code, Physical CPU
    int, int,          # 2B  - CPU state, Application ID
    int, int,          # 2I  - mbox msg MP->AP, mbox msg AP->MP
    int, int,          # 2B  - mbox command MP->AP, mbox command AP->MP
    int,               # H   - SW error count (saturating)
    int, int, int,     # 3I  - SW source filename, Source line, Time of loading
    bytes,             # 16s - Application name
    int, int,          # 2I  - IO buffer in SDRAM (or 0)
    #                    16x - Padding
    int, int, int, int]  # 4I- User0, User1, User2, User3
_REGISTERS_PATTERN = struct.Struct("<IIIIIIII")


class CPUInfo(object):
    """
    Represents information about the state of a CPU.

    This is the content of the `vcpu_t` for the processor, maintained by SARK.
    """
    __slots__ = [
        "_application_id",
        "_application_mailbox_command",
        "__app_mailbox",
        "_application_name",
        "_iobuf_address",
        "__lr",
        "_monitor_mailbox_command",
        "__monitor_mailbox",
        "_physical_cpu_id",
        "__processor_state_register",
        "_registers",
        "_run_time_error",
        "_software_error_count",
        "__filename_address",
        "__line_number",
        "_software_version",
        "__sp",
        "_state",
        "__time",
        "_user",
        "_x", "_y", "_p"]

    def __init__(self, x: int, y: int, p: int, cpu_data: _vcpu_t):
        """
        :param int x: The x-coordinate of a chip
        :param int y: The y-coordinate of a chip
        :param int p: The ID of a core on the chip
        :param tuple cpu_data: A byte-string received from SDRAM on the board
        """
        # pylint: disable=too-many-arguments
        self._x, self._y, self._p = x, y, p

        (registers,  # 32s 0
         self.__processor_state_register, self.__sp, self.__lr,  # 3I  32
         run_time_error, self._physical_cpu_id,  # 2B  44
         state, self._application_id,  # 2B  46
         self.__app_mailbox, self.__monitor_mailbox,  # 2I  48
         app_mailbox_cmd, mon_mailbox_cmd,  # 2B  56
         self._software_error_count,  # H   58
         self.__filename_address, self.__line_number, self.__time,  # 3I  60
         app_name,  # 16s 72
         self._iobuf_address, self._software_version,  # 2I  88
         # skipped                                                  # 16x 96
         user0, user1, user2, user3                                 # 4I  112
         ) = cpu_data

        index = app_name.find(b'\0')
        if index != -1:
            app_name = app_name[:index]
        self._application_name = app_name.decode('ascii')

        self._registers: Sequence[int] = _REGISTERS_PATTERN.unpack(registers)
        self._run_time_error = RunTimeError(run_time_error)
        self._state = CPUState(state)

        self._application_mailbox_command = MailboxCommand(app_mailbox_cmd)
        self._monitor_mailbox_command = MailboxCommand(mon_mailbox_cmd)
        self._user = (user0, user1, user2, user3)

    @property
    def x(self) -> int:
        """
        The X-coordinate of the chip containing the core.

        :return: The x-coordinate of the chip
        :rtype: int
        """
        return self._x

    @property
    def y(self) -> int:
        """
        The y-coordinate of the chip containing the core.

        :return: The y-coordinate of the chip
        :rtype: int
        """
        return self._y

    @property
    def p(self) -> int:
        """
        The ID of the core on the chip.

        :return: The ID of the core
        :rtype: int
        """
        return self._p

    @property
    def state(self) -> CPUState:
        """
        The current state of the core.

        :return: The state of the core
        :rtype: CPUState
        """
        return self._state

    @property
    def physical_cpu_id(self) -> int:
        """
        The physical ID of this processor.

        :return: The physical ID of the processor
        :rtype: int
        """
        return self._physical_cpu_id

    @property
    def application_name(self) -> str:
        """
        The name of the application running on the core.

        :return: The name of the application
        :rtype: str
        """
        return self._application_name

    @property
    def application_id(self) -> int:
        """
        The ID of the application running on the core.

        :return: The ID of the application
        :rtype: int
        """
        return self._application_id

    @property
    def time(self) -> int:
        """
        The time at which the application started.

        :return: The time in seconds since 00:00:00 on the 1st January 1970
        :rtype: int
        """
        return self.__time

    @property
    def run_time_error(self) -> RunTimeError:
        """
        The reason for a run time error.

        :return: The run time error
        :rtype: RunTimeError
        """
        return self._run_time_error

    @property
    def application_mailbox_command(self) -> MailboxCommand:
        """
        The command currently in the mailbox being sent from the monitor
        processor to the application.

        :return: The command
        :rtype: MailboxCommand
        """
        return self._application_mailbox_command

    @property
    def application_mailbox_data_address(self) -> int:
        """
        The address of the data in SDRAM for the application mailbox.

        :return: The address of the data
        :rtype: int
        """
        return self.__app_mailbox

    @property
    def monitor_mailbox_command(self) -> MailboxCommand:
        """
        The command currently in the mailbox being sent from the
        application to the monitor processor.

        :return: The command
        :rtype: MailboxCommand
        """
        return self._monitor_mailbox_command

    @property
    def monitor_mailbox_data_address(self) -> int:
        """
        The address of the data in SDRAM of the monitor mailbox.

        :return: The address of the data
        :rtype: int
        """
        return self.__monitor_mailbox

    @property
    def software_error_count(self) -> int:
        """
        The number of software errors counted. Saturating.

        :return: The number of software errors
        :rtype: int
        """
        return self._software_error_count

    @property
    def software_source_filename_address(self) -> int:
        """
        The address of the filename of the software source.

        :return: The filename address
        :rtype: int
        """
        return self.__filename_address

    @property
    def software_source_line_number(self) -> int:
        """
        The line number of the software source.

        :return: The line number
        :rtype: int
        """
        return self.__line_number

    @property
    def processor_state_register(self) -> int:
        """
        The value in the processor state register (PSR).

        :return: The PSR value
        :rtype: int
        """
        return self.__processor_state_register

    @property
    def stack_pointer(self) -> int:
        """
        The current stack pointer value (SP).

        :return: The SP value
        :rtype: int
        """
        return self.__sp

    @property
    def link_register(self) -> int:
        """
        The current link register value (LR).

        :return: The LR value
        :rtype: int
        """
        return self.__lr

    @property
    def registers(self) -> Sequence[int]:
        """
        The current register values (r0 - r7).

        :return: An array of 8 values, one for each register
        :rtype: list(int)
        """
        return self._registers

    @property
    def user(self) -> Sequence[int]:
        """
        The current user values (user0 - user3).

        :return: An array of 4 values, one for each user value
        :rtype: list(int)
        """
        return self._user

    @property
    def iobuf_address(self) -> int:
        """
        The address of the IOBUF buffer in SDRAM.

        :return: The address
        :rtype: int
        """
        return self._iobuf_address

    @property
    def software_version(self) -> int:
        """
        The software version.

        :return: The software version
        :rtype: int
        """
        return self._software_version

    def __str__(self) -> str:
        return "{}:{}:{:02n} ({:02n}) {:18} {:16s} {:3n}".format(
            self.x, self.y, self.p, self.physical_cpu_id, self._state.name,
            self._application_name, self._application_id)

    def get_status_string(self) -> str:
        """
        Get a string indicating the status of the given core.

        :rtype: str
        """
        if self.state == CPUState.RUN_TIME_EXCEPTION:
            return (
                f"{self._x}:{self._y}:{self._p} "
                f"(ph: {self._physical_cpu_id}) "
                f"in state {self._state.name}:{self._run_time_error.name}\n"
                f"    r0={self._registers[0]}, r1={self._registers[1]}, "
                f"r2={self._registers[2]}, r3={self._registers[3]}\n"
                f"    r4={self._registers[4]}, r5={self._registers[5]}, "
                f"r6={self._registers[6]}, r7={self._registers[7]}\n"
                f"    PSR={self.__processor_state_register}, "
                f"SP={self._stack_pointer}, LR={self._link_register}\n")
        else:
            return (
                f"{self._x}:{self._y}:{self._p} in state {self._state.name}\n")

    @staticmethod
    def mock_info(
            x: int, y: int, p: int, physical_cpu_id: int, state: CPUState):
        """
        Makes a CPU_info object for Testing purposes

        :param int x:
        :param int y:
        :param int p:
        :param int physical_cpu_id:
        :param CPUState CPIstate:
        """
        registers = b'@\x00\x07\x08\xff\x00\x00\x00\x00\x00\x80\x00\xad\x00' \
                    b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' \
                    b'\x00\x00\x00\x00\x00'
        time = 1687857627
        application_name = b'scamp-3\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        iobuff_address = 197634
        cpu_data = (
            registers, 0, 0, 0, 0, physical_cpu_id, state.value, 0, 0, 0, 0,
            0, 0, 0, 0, time, application_name, iobuff_address, 0, 0, 0, 0, 0)
        return CPUInfo(x, y, p, cpu_data)
