import unittest
from spinnman.messages.scp.scp_iptag_command import SCPIPTagCommand
from spinnman.messages.scp.scp_command import SCPCommand
from spinnman.messages.scp.scp_result import SCPResult
from spinnman.messages.scp.scp_signal import SCPSignal

class TestSCPEnums(unittest.TestCase):
    def test_iptag(self):
        self.assertEqual(SCPIPTagCommand.NEW.value, 0)
        self.assertEqual(SCPIPTagCommand.SET.value, 1)
        self.assertEqual(SCPIPTagCommand.GET.value, 2)
        self.assertEqual(SCPIPTagCommand.CLR.value, 3)
        self.assertEqual(SCPIPTagCommand.TTO.value, 4)

    def test_command(self):
        self.assertEqual(SCPCommand.CMD_VER.value, 0)
        self.assertEqual(SCPCommand.CMD_RUN.value, 1)
        self.assertEqual(SCPCommand.CMD_READ.value, 2)
        self.assertEqual(SCPCommand.CMD_WRITE.value, 3)
        self.assertEqual(SCPCommand.CMD_APLX.value, 4)
        
        self.assertEqual(SCPCommand.CMD_FILL.value, 5)
        self.assertEqual(SCPCommand.CMD_REMAP.value, 16)
        self.assertEqual(SCPCommand.CMD_LINK_READ.value, 17)
        self.assertEqual(SCPCommand.CMD_LINK_WRITE.value, 18)
        self.assertEqual(SCPCommand.CMD_AR.value, 19)
        
        self.assertEqual(SCPCommand.CMD_NNP.value, 20)
        self.assertEqual(SCPCommand.CMD_P2PC.value, 21)
        self.assertEqual(SCPCommand.CMD_SIG.value, 22)
        self.assertEqual(SCPCommand.CMD_FFD.value, 23)
        self.assertEqual(SCPCommand.CMD_AS.value, 24)
        
        self.assertEqual(SCPCommand.CMD_LED.value, 25)
        self.assertEqual(SCPCommand.CMD_IPTAG.value, 26)
        self.assertEqual(SCPCommand.CMD_SROM.value, 27)
        self.assertEqual(SCPCommand.CMD_ALLOC.value, 28)

        self.assertEqual(SCPCommand.CMD_RTR.value, 29)
        self.assertEqual(SCPCommand.CMD_FLASH_COPY.value, 49)
        self.assertEqual(SCPCommand.CMD_FLASH_ERASE.value, 50)
        self.assertEqual(SCPCommand.CMD_FLASH_WRITE.value, 51)
        self.assertEqual(SCPCommand.CMD_RESET.value, 55)

        self.assertEqual(SCPCommand.CMD_POWER.value, 57)
        self.assertEqual(SCPCommand.CMD_TUBE.value, 64)


    def test_result(self):
        self.assertEqual(SCPResult.RC_OK.value, 0x80)
        self.assertEqual(SCPResult.RC_LEN.value, 0x81)
        self.assertEqual(SCPResult.RC_SUM.value, 0x82)
        self.assertEqual(SCPResult.RC_CMD.value, 0x83)
        self.assertEqual(SCPResult.RC_ARG.value, 0x84)

        self.assertEqual(SCPResult.RC_PORT.value, 0x85)
        self.assertEqual(SCPResult.RC_TIMEOUT.value, 0x86)
        self.assertEqual(SCPResult.RC_ROUTE.value, 0x87)
        self.assertEqual(SCPResult.RC_CPU.value, 0x88)
        self.assertEqual(SCPResult.RC_DEAD.value, 0x89)

        self.assertEqual(SCPResult.RC_BUF.value, 0x8A)
        self.assertEqual(SCPResult.RC_P2P_NOREPLY.value, 0x8B)
        self.assertEqual(SCPResult.RC_P2P_REJECT.value, 0x8C)
        self.assertEqual(SCPResult.RC_P2P_BUSY.value, 0x8D)
        self.assertEqual(SCPResult.RC_P2P_TIMEOUT.value, 0x8E)

        self.assertEqual(SCPResult.RC_PKT_TX.value, 0x8F)


    def test_signal(self):
        self.assertEqual(SCPSignal.INITIALISE.value, 0)
        self.assertEqual(SCPSignal.POWER_DOWN.value, 1)
        self.assertEqual(SCPSignal.STOP.value, 2)
        self.assertEqual(SCPSignal.START.value, 3)
        self.assertEqual(SCPSignal.SYNC0.value, 4)
        
        self.assertEqual(SCPSignal.SYNC1.value, 5)
        self.assertEqual(SCPSignal.PAUSE.value, 6)
        self.assertEqual(SCPSignal.CONTINUE.value, 7)
        self.assertEqual(SCPSignal.EXIT.value, 8)
        self.assertEqual(SCPSignal.TIMER.value, 9)
        
        self.assertEqual(SCPSignal.USER_0.value, 10)
        self.assertEqual(SCPSignal.USER_1.value, 11)
        self.assertEqual(SCPSignal.USER_2.value, 12)
        self.assertEqual(SCPSignal.USER_3.value, 13)

        self.assertEqual(SCPSignal.INITIALISE.signal_type, 2)
        self.assertEqual(SCPSignal.POWER_DOWN.signal_type, 2)
        self.assertEqual(SCPSignal.STOP.signal_type, 2)
        self.assertEqual(SCPSignal.START.signal_type, 2)
        self.assertEqual(SCPSignal.SYNC0.signal_type, 0)

        self.assertEqual(SCPSignal.SYNC1.signal_type, 0)
        self.assertEqual(SCPSignal.PAUSE.signal_type, 0)
        self.assertEqual(SCPSignal.CONTINUE.signal_type, 0)
        self.assertEqual(SCPSignal.EXIT.signal_type, 2)
        self.assertEqual(SCPSignal.TIMER.signal_type, 0)

        self.assertEqual(SCPSignal.USER_0.signal_type, 0)
        self.assertEqual(SCPSignal.USER_1.signal_type, 0)
        self.assertEqual(SCPSignal.USER_2.signal_type, 0)
        self.assertEqual(SCPSignal.USER_3.signal_type, 0)


if __name__ == '__main__':
    unittest.main()
