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
from spinnman.messages.scp.enums import IPTagCommand
from spinnman.messages.scp.enums import SCPCommand
from spinnman.messages.scp.enums import SCPResult
from spinnman.messages.scp.enums import Signal
from spinnman.messages.scp.enums.signal import SignalType


class TestSCPEnums(unittest.TestCase):
    def test_iptag(self):
        self.assertEqual(IPTagCommand.NEW.value, 0)
        self.assertEqual(IPTagCommand.SET.value, 1)
        self.assertEqual(IPTagCommand.GET.value, 2)
        self.assertEqual(IPTagCommand.CLR.value, 3)
        self.assertEqual(IPTagCommand.TTO.value, 4)

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

        self.assertEqual(SCPCommand.CMD_BMP_POWER.value, 57)
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
        self.assertEqual(Signal.INITIALISE.value, 0)
        self.assertEqual(Signal.POWER_DOWN.value, 1)
        self.assertEqual(Signal.STOP.value, 2)
        self.assertEqual(Signal.START.value, 3)
        self.assertEqual(Signal.SYNC0.value, 4)

        self.assertEqual(Signal.SYNC1.value, 5)
        self.assertEqual(Signal.PAUSE.value, 6)
        self.assertEqual(Signal.CONTINUE.value, 7)
        self.assertEqual(Signal.EXIT.value, 8)
        self.assertEqual(Signal.TIMER.value, 9)

        self.assertEqual(Signal.USER_0.value, 10)
        self.assertEqual(Signal.USER_1.value, 11)
        self.assertEqual(Signal.USER_2.value, 12)
        self.assertEqual(Signal.USER_3.value, 13)

        self.assertEqual(Signal.INITIALISE.signal_type,
                         SignalType.NEAREST_NEIGHBOUR)
        self.assertEqual(Signal.POWER_DOWN.signal_type,
                         SignalType.NEAREST_NEIGHBOUR)
        self.assertEqual(Signal.STOP.signal_type,
                         SignalType.NEAREST_NEIGHBOUR)
        self.assertEqual(Signal.START.signal_type,
                         SignalType.NEAREST_NEIGHBOUR)

        self.assertEqual(Signal.SYNC0.signal_type,
                         SignalType.MULTICAST)
        self.assertEqual(Signal.SYNC1.signal_type,
                         SignalType.MULTICAST)
        self.assertEqual(Signal.PAUSE.signal_type,
                         SignalType.MULTICAST)
        self.assertEqual(Signal.CONTINUE.signal_type,
                         SignalType.MULTICAST)
        self.assertEqual(Signal.EXIT.signal_type,
                         SignalType.MULTICAST)
        self.assertEqual(Signal.TIMER.signal_type,
                         SignalType.MULTICAST)

        self.assertEqual(Signal.USER_0.signal_type,
                         SignalType.MULTICAST)
        self.assertEqual(Signal.USER_1.signal_type,
                         SignalType.MULTICAST)
        self.assertEqual(Signal.USER_2.signal_type,
                         SignalType.MULTICAST)
        self.assertEqual(Signal.USER_3.signal_type,
                         SignalType.MULTICAST)


if __name__ == '__main__':
    unittest.main()
