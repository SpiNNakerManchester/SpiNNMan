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
from typing import Final, Sequence, Tuple
from typing_extensions import TypeAlias
from spinnman.model.enums import CPUState, RunTimeError, MailboxCommand

#: Size of `vcpu_t` in SARK.
CPU_INFO_BYTES = 128
CPU_USER_0_START_ADDRESS = 112
#: Offset into data of byte of processor state field.
STATE_FIELD_OFFSET = 48

#: Corresponds to vcpu_t in sark.h
_VCPU_PATTERN = struct.Struct("< 32s 3I 2B 2B 2I 2B H 3I 16s 2I 16x 4I")
VCPU_T: Final['TypeAlias'] = Tuple[
    # pylint: disable=wrong-spelling-in-comment
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
        "__application_id",
        "__application_mailbox_command",
        "__app_mailbox",
        "__application_name",
        "__iobuf_address",
        "__link_register",
        "__monitor_mailbox_command",
        "__monitor_mailbox",
        "__physical_cpu_id",
        "__processor_state_register",
        "__registers",
        "__run_time_error",
        "__run_time_error_value",
        "__software_error_count",
        "__filename_address",
        "__line_number",
        "__software_version",
        "__stack_pointer",
        "__state",
        "__time",
        "__user",
        "__x", "__y", "__p"]

    def __init__(self, x: int, y: int, p: int, cpu_data: VCPU_T):
        """
        :param x: The x-coordinate of a chip
        :param y: The y-coordinate of a chip
        :param p: The ID of a core on the chip
        :param cpu_data: A byte-string received from SDRAM on the board
        """
        self.__x, self.__y, self.__p = x, y, p

        (registers,  # 32s 0
         self.__processor_state_register, self.__stack_pointer,
         self.__link_register,  run_time_error,
         self.__physical_cpu_id,  # 2B  44
         state, self.__application_id,  # 2B  46
         self.__app_mailbox, self.__monitor_mailbox,  # 2I  48
         app_mailbox_cmd, mon_mailbox_cmd,  # 2B  56
         self.__software_error_count,  # H   58
         self.__filename_address, self.__line_number, self.__time,  # 3I  60
         app_name,  # 16s 72
         self.__iobuf_address, self.__software_version,  # 2I  88
         # skipped                                                  # 16x 96
         user0, user1, user2, user3                                 # 4I  112
         ) = cpu_data

        index = app_name.find(b'\0')
        if index != -1:
            app_name = app_name[:index]
        self.__application_name = app_name.decode('ascii')

        self.__registers: Sequence[int] = _REGISTERS_PATTERN.unpack(registers)
        self.__run_time_error_value = run_time_error
        try:
            self.__run_time_error = RunTimeError(run_time_error)
        except ValueError:
            self.__run_time_error = RunTimeError.UNRECOGNISED
        self.__state = CPUState(state)

        self.__application_mailbox_command = MailboxCommand(app_mailbox_cmd)
        self.__monitor_mailbox_command = MailboxCommand(mon_mailbox_cmd)
        self.__user = (user0, user1, user2, user3)

    @property
    def x(self) -> int:
        """
        The X-coordinate of the chip containing the core.
        """
        return self.__x

    @property
    def y(self) -> int:
        """
        The y-coordinate of the chip containing the core.
        """
        return self.__y

    @property
    def p(self) -> int:
        """
        The ID of the core on the chip.
        """
        return self.__p

    @property
    def state(self) -> CPUState:
        """
        The current state of the core.
        """
        return self.__state

    @property
    def physical_cpu_id(self) -> int:
        """
        The physical ID of this processor.
        """
        return self.__physical_cpu_id

    @property
    def application_name(self) -> str:
        """
        The name of the application running on the core.
        """
        return self.__application_name

    @property
    def application_id(self) -> int:
        """
        The ID of the application running on the core.
        """
        return self.__application_id

    @property
    def time(self) -> int:
        """
        The time at which the application started.
        """
        return self.__time

    @property
    def run_time_error(self) -> RunTimeError:
        """
        The reason for a run time error.
        """
        return self.__run_time_error

    @property
    def application_mailbox_command(self) -> MailboxCommand:
        """
        The command currently in the mailbox being sent from the monitor
        processor to the application.
        """
        return self.__application_mailbox_command

    @property
    def application_mailbox_data_address(self) -> int:
        """
        The address of the data in SDRAM for the application mailbox.
        """
        return self.__app_mailbox

    @property
    def monitor_mailbox_command(self) -> MailboxCommand:
        """
        The command currently in the mailbox being sent from the
        application to the monitor processor.
        """
        return self.__monitor_mailbox_command

    @property
    def monitor_mailbox_data_address(self) -> int:
        """
        The address of the data in SDRAM of the monitor mailbox.
        """
        return self.__monitor_mailbox

    @property
    def software_error_count(self) -> int:
        """
        The number of software errors counted. Saturating.
        """
        return self.__software_error_count

    @property
    def software_source_filename_address(self) -> int:
        """
        The address of the filename of the software source.
        """
        return self.__filename_address

    @property
    def software_source_line_number(self) -> int:
        """
        The line number of the software source.
        """
        return self.__line_number

    @property
    def processor_state_register(self) -> int:
        """
        The value in the processor state register.
        """
        return self.__processor_state_register

    @property
    def stack_pointer(self) -> int:
        """
        The current stack pointer value.
        """
        return self.__stack_pointer

    @property
    def link_register(self) -> int:
        """
        The current link register value.
        """
        return self.__link_register

    @property
    def registers(self) -> Sequence[int]:
        """
        The current register values (r0 - r7).
        """
        return self.__registers

    @property
    def user(self) -> Sequence[int]:
        """
        The current user values (user0 - user3).
        """
        return self.__user

    @property
    def iobuf_address(self) -> int:
        """
        The address of the IOBUF buffer in SDRAM.
        """
        return self.__iobuf_address

    @property
    def software_version(self) -> int:
        """
        The software version.
        """
        return self.__software_version

    def __str__(self) -> str:
        return (f"{self.x}:{self.y}:{self.p:02n} ({self.physical_cpu_id:02n}) "
                f"{self.__state.name:18} {self.__application_name:16s} "
                f"{self.__application_id:3n}")

    def get_status_string(self) -> str:
        """
        :returns: A string indicating the status of the given core.
        """
        if self.state == CPUState.RUN_TIME_EXCEPTION:
            rte_string = f"{self.run_time_error.name}"
            if self.run_time_error == RunTimeError.UNRECOGNISED:
                rte_string += f" ({self.__run_time_error_value})"
            return (
                f"{self.__x}:{self.__y}:{self.__p} "
                f"(ph: {self.__physical_cpu_id}) "
                f"in state {self.__state.name}:{rte_string}\n"
                f"    r0={self.__registers[0]}, r1={self.__registers[1]}, "
                f"r2={self.__registers[2]}, r3={self.__registers[3]}\n"
                f"    r4={self.__registers[4]}, r5={self.__registers[5]}, "
                f"r6={self.__registers[6]}, r7={self.__registers[7]}\n"
                f"    PSR={self.__processor_state_register}, "
                f"SP={self.__stack_pointer}, LR={self.__link_register}\n")
        else:
            return (
                f"{self.__x}:{self.__y}:{self.__p} "
                f"in state {self.__state.name}\n")

    @staticmethod
    def mock_info(x: int, y: int, p: int, physical_cpu_id: int,
                  state: CPUState) -> "CPUInfo":
        """
        Makes a CPU_info object for Testing purposes

        :returns: A fake
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
