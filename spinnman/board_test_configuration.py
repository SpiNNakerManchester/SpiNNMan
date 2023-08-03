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

import unittest
from spinn_utilities.config_holder import set_config
from spinn_utilities.ping import Ping
# from spinnman.model import BMPConnectionData

_LOCALHOST = "127.0.0.1"
# Microsoft invalid IP address. For more details see:
# https://answers.microsoft.com/en-us/windows/forum/windows_vista-networking/invalid-ip-address-169254xx/ce096728-e2b7-4d54-80cc-52a4ed342870
_NOHOST = "169.254.254.254"
_PORT = 54321


class BoardTestConfiguration(object):

    def __init__(self):
        self.localport = None
        self.remotehost = None
        self.board_version = None
        self.bmp_names = None
        self.auto_detect_bmp = None

    def set_up_local_virtual_board(self):
        self.localport = _PORT
        self.remotehost = _LOCALHOST
        self.board_version = 5

    def set_up_remote_board(self):
        if Ping.host_is_reachable("192.168.240.253"):
            self.remotehost = "192.168.240.253"
            self.board_version = 3
            set_config("Machine", "version", 3)
            self.auto_detect_bmp = False
        elif Ping.host_is_reachable("spinn-4.cs.man.ac.uk"):
            self.remotehost = "spinn-4.cs.man.ac.uk"
            self.board_version = 5
            set_config("Machine", "version", 5)
        elif Ping.host_is_reachable("192.168.240.1"):
            self.remotehost = "192.168.240.1"
            self.board_version = 5
            set_config("Machine", "version", 5)
        else:
            raise unittest.SkipTest("None of the test boards reachable")

        # it always was None but this is what to do if not
        #  self.bmp_names = BMPConnectionData(0, 0, self.bmp_names, [0], None)

    def set_up_nonexistent_board(self):
        self.localport = _PORT
        self.remotehost = _NOHOST
        self.board_version = None
