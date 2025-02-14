# Copyright (c) 2023 The University of Manchester
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

import unittest
from spinnman.connections.udp_packet_connections import SCAMPConnection
from spinnman.processes import MostDirectConnectionSelector


class TestCpuInfos(unittest.TestCase):

    def test_empty(self) -> None:
        with self.assertRaises(StopIteration):
            MostDirectConnectionSelector([])

    def test_one(self) -> None:
        c = SCAMPConnection(local_host="127.0.0.0")
        MostDirectConnectionSelector([c])
