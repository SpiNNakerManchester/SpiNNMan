# Copyright (c) 2015 The University of Manchester
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

from typing import Optional
import unittest
from spinn_utilities.config_holder import set_config
from spinn_utilities.ping import Ping
from spinnman.constants import LOCAL_HOST


class BoardTestConfiguration(object):
    """
    Configuration to use for a test board
    """

    def __init__(self) -> None:
        self.remotehost: str = "UNSET"
        self.auto_detect_bmp: bool = False

    def set_up_remote_board(self, version: Optional[int] = None) -> None:
        """
        Gets a remote board to test, returning the first that it finds.

        Search order is
        - Local 4 Chip board
        - 48 Chip board "spinn-4.cs.man.ac.uk"
        - Local 48 Chip board if at 192.168.240.1
        - Virtual machine

        The first three ignore the version param the last needs it

        Sets the version field in the configs.

        :param version: Version for a virtual if no physical board found
        :raises unittest.SkipTest:
            If no physical machine found and no version provided
        """
        if Ping.host_is_reachable("192.168.240.253"):
            self.remotehost = "192.168.240.253"
            set_config("Machine", "version", "3")
            self.auto_detect_bmp = False
        elif Ping.host_is_reachable("spinn-4.cs.man.ac.uk"):
            self.remotehost = "spinn-4.cs.man.ac.uk"
            set_config("Machine", "version", "5")
        elif Ping.host_is_reachable("192.168.240.1"):
            self.remotehost = "192.168.240.1"
            set_config("Machine", "version", "5")
        elif version is not None:
            self.remotehost = LOCAL_HOST
            set_config("Machine", "version", str(version))
        else:
            raise unittest.SkipTest("None of the test boards reachable")
