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
from spinnman.model import CPUInfo, CPUInfos
from spinnman.model.enums.cpu_state import CPUState


class TestCpuInfos(unittest.TestCase):

    def setUp(self):
        unittest_setup()

    def make_info_data(self, physical_cpu_id, state):
        registers = b'@\x00\x07\x08\xff\x00\x00\x00\x00\x00\x80\x00\xad\x00' \
                    b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' \
                    b'\x00\x00\x00\x00\x00'
        time = 1687857627
        application_name = b'scamp-3\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        iobuff_address = 197634
        return (registers, 0, 0, 0, 0, physical_cpu_id, state.value, 0, 0, 0,
                0, 0, 0, 0, 0, time, application_name, iobuff_address, 0, 0,
                0, 0, 0)

    def test_cpu_infos(self):
        infos = CPUInfos()

        info = CPUInfo(0, 0, 1, self.make_info_data(5, CPUState.RUNNING))
        infos.add_info(info)
        info = CPUInfo(0, 0, 2, self.make_info_data(6, CPUState.FINISHED))
        infos.add_info(info)
        info = CPUInfo(1, 0, 1, self.make_info_data(7, CPUState.FINISHED))
        infos.add_info(info)
        info = CPUInfo(1, 1, 2, self.make_info_data(4, CPUState.RUN_TIME_EXCEPTION))
        infos.add_info(info)

        self.assertSetEqual(set(infos), {(1, 0, 1), (0, 0, 1), (0, 0, 2), (1, 1, 2)})
        self.assertEqual(
            "['0, 0, 1 (ph: 5)', '0, 0, 2 (ph: 6)', '1, 0, 1 (ph: 7)', '1, 1, 2 (ph: 4)']",
            str(infos))

        finished = infos.infos_for_state(CPUState.FINISHED)
        self.assertEqual(
            "['0, 0, 2 (ph: 6)', '1, 0, 1 (ph: 7)']", str(finished))
        self.assertTrue(finished)

        idle = infos.infos_for_state(CPUState.IDLE)
        self.assertFalse(idle)

        info = infos.get_cpu_info(0, 0, 2)
        self.assertEqual(
            "0:0:02 (06) FINISHED           scamp-3            0", str(info))

        self.assertEqual(infos.get_status_string(),
                         "0:0:1 in state RUNNING\n"
                         "0:0:2 in state FINISHED\n"
                         "1:0:1 in state FINISHED\n"
                         "1:1:2 (ph: 4) in state RUN_TIME_EXCEPTION:NONE\n"
                         "    r0=134676544, r1=255, r2=8388608, r3=173\n"
                         "    r4=0, r5=0, r6=0, r7=0\n"
                         "    PSR=0, SP=0, LR=0\n")


if __name__ == '__main__':
    unittest.main()