from spynnaker.pyNN.utilities.conf import config

import socket


class BoardTestConfiguration(object):
    def __init__(self):
        self.localhost = None
        self.localport = None
        self.remotehost = None
        self.board_version = None

    def set_up_local_virtual_board(self):
        self.localhost = "127.0.0.1"
        self.localport = 54321
        self.remotehost = "127.0.0.1"
        self.board_version = config.getint("Machine", "version")

    def set_up_remote_board(self):
        # self.localhost = None
        self.localport = 54321
        self.remotehost = config.get("Machine", "machineName")
        self.board_version = config.getint("Machine", "version")
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((self.remotehost, 0))
        self.localhost = s.getsockname()[0]

    def set_up_nonexistent_board(self):
        self.localhost = None
        self.localport = 54321
        # Microsoft invalid IP address. For more details see:
        # http://answers.microsoft.com/en-us/windows/forum/windows_vista-networking/invalid-ip-address-169254xx/ce096728-e2b7-4d54-80cc-52a4ed342870
        self.remotehost = "169.254.254.254"
        self.board_version = config.getint("Machine", "version")