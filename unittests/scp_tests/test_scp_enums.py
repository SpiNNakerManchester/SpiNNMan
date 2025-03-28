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

import unittest
from spinnman.config_setup import unittest_setup
from spinnman.messages.scp.enums import IPTagCommand
from spinnman.messages.scp.enums import SCPCommand
from spinnman.messages.scp.enums import SCPResult
from spinnman.messages.scp.enums import Signal
from spinnman.messages.scp.enums.signal import SignalType


class TestSCPEnums(unittest.TestCase):

    def setUp(self) -> None:
        unittest_setup()

    def test_iptag(self) -> None:
        self.assertEqual(IPTagCommand.NEW.value, 0)
        self.assertEqual(IPTagCommand.SET.value, 1)
        self.assertEqual(IPTagCommand.GET.value, 2)
        self.assertEqual(IPTagCommand.CLR.value, 3)
        self.assertEqual(IPTagCommand.TTO.value, 4)

    def test_command(self) -> None:
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
        self.assertEqual(SCPCommand.CMD_APP_COPY_RUN.value, 21)
        self.assertEqual(SCPCommand.CMD_SIG.value, 22)
        self.assertEqual(SCPCommand.CMD_FFD.value, 23)
        self.assertEqual(SCPCommand.CMD_AS.value, 24)

        self.assertEqual(SCPCommand.CMD_LED.value, 25)
        self.assertEqual(SCPCommand.CMD_IPTAG.value, 26)
        self.assertEqual(SCPCommand.CMD_SROM.value, 27)
        self.assertEqual(SCPCommand.CMD_ALLOC.value, 28)

        self.assertEqual(SCPCommand.CMD_RTR.value, 29)
        self.assertEqual(SCPCommand.CMD_SYNC.value, 32)
        self.assertEqual(SCPCommand.CMD_FLASH_COPY.value, 49)
        self.assertEqual(SCPCommand.CMD_FLASH_ERASE.value, 50)
        self.assertEqual(SCPCommand.CMD_FLASH_WRITE.value, 51)
        self.assertEqual(SCPCommand.CMD_RESET.value, 55)

        self.assertEqual(SCPCommand.CMD_BMP_POWER.value, 57)
        self.assertEqual(SCPCommand.CMD_TUBE.value, 64)

    def test_result(self) -> None:
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

    def test_signal(self) -> None:
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
                         SignalType.MULTICAST)
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
