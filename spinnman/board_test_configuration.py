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

import configparser
from contextlib import closing
import os
import socket
import unittest
from spinn_utilities.ping import Ping
from spinnman.model import BMPConnectionData

_LOCALHOST = "127.0.0.1"
# Microsoft invalid IP address. For more details see:
# https://answers.microsoft.com/en-us/windows/forum/windows_vista-networking/invalid-ip-address-169254xx/ce096728-e2b7-4d54-80cc-52a4ed342870
_NOHOST = "169.254.254.254"
_PORT = 54321


class BoardTestConfiguration(object):

    def __init__(self):
        self.localhost = None
        self.localport = None
        self.remotehost = None
        self.board_version = None
        self.bmp_names = None
        self.auto_detect_bmp = None

        self._config = configparser.RawConfigParser()
        config_file = os.path.join(
            os.path.dirname(__file__), "board_test_configuration.cfg")
        self._config.read(config_file)

    def set_up_local_virtual_board(self):
        self.localhost = _LOCALHOST
        self.localport = _PORT
        self.remotehost = _LOCALHOST
        self.board_version = self._config.getint("Machine", "version")

    def set_up_remote_board(self):
        self.remotehost = self._config.get("Machine", "machineName")
        if not Ping.host_is_reachable(self.remotehost):
            raise unittest.SkipTest("test board appears to be down")
        self.board_version = self._config.getint("Machine", "version")
        self.bmp_names = self._config.get("Machine", "bmp_names")
        if self.bmp_names == "None":
            self.bmp_names = None
        else:
            self.bmp_names = [BMPConnectionData(
                0, 0, self.bmp_names, [0], None)]
        self.auto_detect_bmp = \
            self._config.getboolean("Machine", "auto_detect_bmp")
        self.localport = _PORT
        with closing(socket.socket(socket.AF_INET, socket.SOCK_DGRAM)) as s:
            s.connect((self.remotehost, _PORT))
            self.localhost = s.getsockname()[0]

    def set_up_nonexistent_board(self):
        self.localhost = None
        self.localport = _PORT
        self.remotehost = _NOHOST
        self.board_version = self._config.getint("Machine", "version")
