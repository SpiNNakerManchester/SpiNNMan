import unittest
from spinnman.model.enums import MailboxCommand, CPUState, RunTimeError
from spinnman.constants import ROUTER_REGISTER_REGISTERS


class TestingEnums(unittest.TestCase):
    def test_mailbox_command_enum(self):
        self.assertEquals(MailboxCommand.SHM_IDLE.value, 0)
        self.assertEquals(MailboxCommand.SHM_MSG.value, 1)
        self.assertEquals(MailboxCommand.SHM_NOP.value, 2)
        self.assertEquals(MailboxCommand.SHM_SIGNAL.value, 3)
        self.assertEquals(MailboxCommand.SHM_CMD.value, 4)

    def test_cpu_state_enum(self):
        self.assertEquals(CPUState.DEAD.value, 0)
        self.assertEquals(CPUState.POWERED_DOWN.value, 1)
        self.assertEquals(CPUState.RUN_TIME_EXCEPTION.value, 2)
        self.assertEquals(CPUState.WATCHDOG.value, 3)
        self.assertEquals(CPUState.INITIALISING.value, 4)

        self.assertEquals(CPUState.READY.value, 5)
        self.assertEquals(CPUState.C_MAIN.value, 6)
        self.assertEquals(CPUState.RUNNING.value, 7)
        self.assertEquals(CPUState.SYNC0.value, 8)
        self.assertEquals(CPUState.SYNC1.value, 9)

        self.assertEquals(CPUState.PAUSED.value, 10)
        self.assertEquals(CPUState.FINISHED.value, 11)
        self.assertEquals(CPUState.IDLE.value, 15)

    def test_run_time_error_enum(self):
        self.assertEquals(RunTimeError.NONE.value, 0)
        self.assertEquals(RunTimeError.RESET.value, 1)
        self.assertEquals(RunTimeError.UNDEF.value, 2)
        self.assertEquals(RunTimeError.SVC.value, 3)
        self.assertEquals(RunTimeError.PABT.value, 4)

        self.assertEquals(RunTimeError.DABT.value, 5)
        self.assertEquals(RunTimeError.IRQ.value, 6)
        self.assertEquals(RunTimeError.FIQ.value, 7)
        self.assertEquals(RunTimeError.VIC.value, 8)
        self.assertEquals(RunTimeError.ABORT.value, 9)

        self.assertEquals(RunTimeError.MALLOC.value, 10)
        self.assertEquals(RunTimeError.DIVBY0.value, 11)
        self.assertEquals(RunTimeError.EVENT.value, 12)
        self.assertEquals(RunTimeError.SWERR.value, 13)
        self.assertEquals(RunTimeError.IOBUF.value, 14)

    def test_router_diagnostics_enum(self):
        self.assertEquals(ROUTER_REGISTER_REGISTERS.LOC_MC.value, 0)
        self.assertEquals(ROUTER_REGISTER_REGISTERS.EXT_MC.value, 1)
        self.assertEquals(ROUTER_REGISTER_REGISTERS.LOC_PP.value, 2)
        self.assertEquals(ROUTER_REGISTER_REGISTERS.EXT_PP.value, 3)
        self.assertEquals(ROUTER_REGISTER_REGISTERS.LOC_NN.value, 4)

        self.assertEquals(ROUTER_REGISTER_REGISTERS.EXT_NN.value, 5)
        self.assertEquals(ROUTER_REGISTER_REGISTERS.LOC_FR.value, 6)
        self.assertEquals(ROUTER_REGISTER_REGISTERS.EXT_FR.value, 7)
        self.assertEquals(ROUTER_REGISTER_REGISTERS.DUMP_MC.value, 8)
        self.assertEquals(ROUTER_REGISTER_REGISTERS.DUMP_PP.value, 9)

        self.assertEquals(ROUTER_REGISTER_REGISTERS.DUMP_NN.value, 10)
        self.assertEquals(ROUTER_REGISTER_REGISTERS.DUMP_FR.value, 11)
        self.assertEquals(ROUTER_REGISTER_REGISTERS.USER_0.value, 12)
        self.assertEquals(ROUTER_REGISTER_REGISTERS.USER_3.value, 15)


if __name__ == '__main__':
    unittest.main()
