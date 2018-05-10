import socket
import os
import platform
import subprocess
import unittest
import time
from six.moves import configparser
from spinnman.model import BMPConnectionData

_LOCALHOST = "127.0.0.1"
# Microsoft invalid IP address. For more details see:
# http://answers.microsoft.com/en-us/windows/forum/windows_vista-networking/invalid-ip-address-169254xx/ce096728-e2b7-4d54-80cc-52a4ed342870
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
        config_file = os.path.join(os.path.dirname(__file__), "test.cfg")
        self._config.read(config_file)

    def set_up_local_virtual_board(self):
        self.localhost = _LOCALHOST
        self.localport = _PORT
        self.remotehost = _LOCALHOST
        self.board_version = self._config.getint("Machine", "version")

    def set_up_remote_board(self):
        self.remotehost = self._config.get("Machine", "machineName")
        if not self.host_is_reachable(self.remotehost):
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
        self.localport = 54321
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect((self.remotehost, 0))
            self.localhost = s.getsockname()[0]
        finally:
            s.close()

    def set_up_nonexistent_board(self):
        self.localhost = None
        self.localport = _PORT
        self.remotehost = _NOHOST
        self.board_version = self._config.getint("Machine", "version")

    @staticmethod
    def host_is_reachable(ipaddr):
        if platform.platform().lower().startswith("windows"):
            cmd = "ping -n 1 -w 1 "
        else:
            cmd = "ping -c 1 -W 1 "
        process = subprocess.Popen(
            cmd + ipaddr, shell=True, stdout=subprocess.PIPE)
        time.sleep(1.2)
        process.stdout.close()
        process.wait()
        return process.returncode == 0
