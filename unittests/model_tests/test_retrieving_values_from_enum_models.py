# Copyright (c) 2017-2019 The University of Manchester
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import unittest
from spinnman.model.enums import MailboxCommand, CPUState, RunTimeError
from spinnman.constants import ROUTER_REGISTER_REGISTERS


class TestingEnums(unittest.TestCase):
    def test_mailbox_command_enum(self):
        self.assertEqual(MailboxCommand.SHM_IDLE.value, 0)
        self.assertEqual(MailboxCommand.SHM_MSG.value, 1)
        self.assertEqual(MailboxCommand.SHM_NOP.value, 2)
        self.assertEqual(MailboxCommand.SHM_SIGNAL.value, 3)
        self.assertEqual(MailboxCommand.SHM_CMD.value, 4)

    def test_cpu_state_enum(self):
        self.assertEqual(CPUState.DEAD.value, 0)
        self.assertEqual(CPUState.POWERED_DOWN.value, 1)
        self.assertEqual(CPUState.RUN_TIME_EXCEPTION.value, 2)
        self.assertEqual(CPUState.WATCHDOG.value, 3)
        self.assertEqual(CPUState.INITIALISING.value, 4)

        self.assertEqual(CPUState.READY.value, 5)
        self.assertEqual(CPUState.C_MAIN.value, 6)
        self.assertEqual(CPUState.RUNNING.value, 7)
        self.assertEqual(CPUState.SYNC0.value, 8)
        self.assertEqual(CPUState.SYNC1.value, 9)

        self.assertEqual(CPUState.PAUSED.value, 10)
        self.assertEqual(CPUState.FINISHED.value, 11)
        self.assertEqual(CPUState.IDLE.value, 15)

    def test_run_time_error_enum(self):
        self.assertEqual(RunTimeError.NONE.value, 0)
        self.assertEqual(RunTimeError.RESET.value, 1)
        self.assertEqual(RunTimeError.UNDEF.value, 2)
        self.assertEqual(RunTimeError.SVC.value, 3)
        self.assertEqual(RunTimeError.PABT.value, 4)

        self.assertEqual(RunTimeError.DABT.value, 5)
        self.assertEqual(RunTimeError.IRQ.value, 6)
        self.assertEqual(RunTimeError.FIQ.value, 7)
        self.assertEqual(RunTimeError.VIC.value, 8)
        self.assertEqual(RunTimeError.ABORT.value, 9)

        self.assertEqual(RunTimeError.MALLOC.value, 10)
        self.assertEqual(RunTimeError.DIVBY0.value, 11)
        self.assertEqual(RunTimeError.EVENT.value, 12)
        self.assertEqual(RunTimeError.SWERR.value, 13)
        self.assertEqual(RunTimeError.IOBUF.value, 14)

    def test_router_diagnostics_enum(self):
        self.assertEqual(ROUTER_REGISTER_REGISTERS.LOC_MC.value, 0)
        self.assertEqual(ROUTER_REGISTER_REGISTERS.EXT_MC.value, 1)
        self.assertEqual(ROUTER_REGISTER_REGISTERS.LOC_PP.value, 2)
        self.assertEqual(ROUTER_REGISTER_REGISTERS.EXT_PP.value, 3)
        self.assertEqual(ROUTER_REGISTER_REGISTERS.LOC_NN.value, 4)

        self.assertEqual(ROUTER_REGISTER_REGISTERS.EXT_NN.value, 5)
        self.assertEqual(ROUTER_REGISTER_REGISTERS.LOC_FR.value, 6)
        self.assertEqual(ROUTER_REGISTER_REGISTERS.EXT_FR.value, 7)
        self.assertEqual(ROUTER_REGISTER_REGISTERS.DUMP_MC.value, 8)
        self.assertEqual(ROUTER_REGISTER_REGISTERS.DUMP_PP.value, 9)

        self.assertEqual(ROUTER_REGISTER_REGISTERS.DUMP_NN.value, 10)
        self.assertEqual(ROUTER_REGISTER_REGISTERS.DUMP_FR.value, 11)
        self.assertEqual(ROUTER_REGISTER_REGISTERS.USER_0.value, 12)
        self.assertEqual(ROUTER_REGISTER_REGISTERS.USER_3.value, 15)


if __name__ == '__main__':
    unittest.main()
