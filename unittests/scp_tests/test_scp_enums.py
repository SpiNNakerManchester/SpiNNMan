import unittest
from spinnman.messages.scp.enums import IPTagCommand
from spinnman.messages.scp.enums import SCPCommand
from spinnman.messages.scp.enums import SCPResult
from spinnman.messages.scp.enums import Signal
from spinnman.messages.scp.enums.signal import SignalType


class TestSCPEnums(unittest.TestCase):
    def test_iptag(self):
        self.assertEquals(IPTagCommand.NEW.value, 0)
        self.assertEquals(IPTagCommand.SET.value, 1)
        self.assertEquals(IPTagCommand.GET.value, 2)
        self.assertEquals(IPTagCommand.CLR.value, 3)
        self.assertEquals(IPTagCommand.TTO.value, 4)

    def test_command(self):
        self.assertEquals(SCPCommand.CMD_VER.value, 0)
        self.assertEquals(SCPCommand.CMD_RUN.value, 1)
        self.assertEquals(SCPCommand.CMD_READ.value, 2)
        self.assertEquals(SCPCommand.CMD_WRITE.value, 3)
        self.assertEquals(SCPCommand.CMD_APLX.value, 4)

        self.assertEquals(SCPCommand.CMD_FILL.value, 5)
        self.assertEquals(SCPCommand.CMD_REMAP.value, 16)
        self.assertEquals(SCPCommand.CMD_LINK_READ.value, 17)
        self.assertEquals(SCPCommand.CMD_LINK_WRITE.value, 18)
        self.assertEquals(SCPCommand.CMD_AR.value, 19)

        self.assertEquals(SCPCommand.CMD_NNP.value, 20)
        self.assertEquals(SCPCommand.CMD_P2PC.value, 21)
        self.assertEquals(SCPCommand.CMD_SIG.value, 22)
        self.assertEquals(SCPCommand.CMD_FFD.value, 23)
        self.assertEquals(SCPCommand.CMD_AS.value, 24)

        self.assertEquals(SCPCommand.CMD_LED.value, 25)
        self.assertEquals(SCPCommand.CMD_IPTAG.value, 26)
        self.assertEquals(SCPCommand.CMD_SROM.value, 27)
        self.assertEquals(SCPCommand.CMD_ALLOC.value, 28)

        self.assertEquals(SCPCommand.CMD_RTR.value, 29)
        self.assertEquals(SCPCommand.CMD_FLASH_COPY.value, 49)
        self.assertEquals(SCPCommand.CMD_FLASH_ERASE.value, 50)
        self.assertEquals(SCPCommand.CMD_FLASH_WRITE.value, 51)
        self.assertEquals(SCPCommand.CMD_RESET.value, 55)

        self.assertEquals(SCPCommand.CMD_BMP_POWER.value, 57)
        self.assertEquals(SCPCommand.CMD_TUBE.value, 64)

    def test_result(self):
        self.assertEquals(SCPResult.RC_OK.value, 0x80)
        self.assertEquals(SCPResult.RC_LEN.value, 0x81)
        self.assertEquals(SCPResult.RC_SUM.value, 0x82)
        self.assertEquals(SCPResult.RC_CMD.value, 0x83)
        self.assertEquals(SCPResult.RC_ARG.value, 0x84)

        self.assertEquals(SCPResult.RC_PORT.value, 0x85)
        self.assertEquals(SCPResult.RC_TIMEOUT.value, 0x86)
        self.assertEquals(SCPResult.RC_ROUTE.value, 0x87)
        self.assertEquals(SCPResult.RC_CPU.value, 0x88)
        self.assertEquals(SCPResult.RC_DEAD.value, 0x89)

        self.assertEquals(SCPResult.RC_BUF.value, 0x8A)
        self.assertEquals(SCPResult.RC_P2P_NOREPLY.value, 0x8B)
        self.assertEquals(SCPResult.RC_P2P_REJECT.value, 0x8C)
        self.assertEquals(SCPResult.RC_P2P_BUSY.value, 0x8D)
        self.assertEquals(SCPResult.RC_P2P_TIMEOUT.value, 0x8E)

        self.assertEquals(SCPResult.RC_PKT_TX.value, 0x8F)

    def test_signal(self):
        self.assertEquals(Signal.INITIALISE.value, 0)
        self.assertEquals(Signal.POWER_DOWN.value, 1)
        self.assertEquals(Signal.STOP.value, 2)
        self.assertEquals(Signal.START.value, 3)
        self.assertEquals(Signal.SYNC0.value, 4)

        self.assertEquals(Signal.SYNC1.value, 5)
        self.assertEquals(Signal.PAUSE.value, 6)
        self.assertEquals(Signal.CONTINUE.value, 7)
        self.assertEquals(Signal.EXIT.value, 8)
        self.assertEquals(Signal.TIMER.value, 9)

        self.assertEquals(Signal.USER_0.value, 10)
        self.assertEquals(Signal.USER_1.value, 11)
        self.assertEquals(Signal.USER_2.value, 12)
        self.assertEquals(Signal.USER_3.value, 13)

        self.assertEquals(Signal.INITIALISE.signal_type,
                         SignalType.NEAREST_NEIGHBOUR)
        self.assertEquals(Signal.POWER_DOWN.signal_type,
                         SignalType.NEAREST_NEIGHBOUR)
        self.assertEquals(Signal.STOP.signal_type,
                         SignalType.NEAREST_NEIGHBOUR)
        self.assertEquals(Signal.START.signal_type,
                         SignalType.NEAREST_NEIGHBOUR)

        self.assertEquals(Signal.SYNC0.signal_type,
                         SignalType.MULTICAST)
        self.assertEquals(Signal.SYNC1.signal_type,
                         SignalType.MULTICAST)
        self.assertEquals(Signal.PAUSE.signal_type,
                         SignalType.MULTICAST)
        self.assertEquals(Signal.CONTINUE.signal_type,
                         SignalType.MULTICAST)
        self.assertEquals(Signal.EXIT.signal_type,
                         SignalType.MULTICAST)
        self.assertEquals(Signal.TIMER.signal_type,
                         SignalType.MULTICAST)

        self.assertEquals(Signal.USER_0.signal_type,
                         SignalType.MULTICAST)
        self.assertEquals(Signal.USER_1.signal_type,
                         SignalType.MULTICAST)
        self.assertEquals(Signal.USER_2.signal_type,
                         SignalType.MULTICAST)
        self.assertEquals(Signal.USER_3.signal_type,
                         SignalType.MULTICAST)


if __name__ == '__main__':
    unittest.main()
