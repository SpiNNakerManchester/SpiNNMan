from spinnman import constants
from spinnman import exceptions


class AbstractIPTAG(object):

    def __init__(self, port):
        self._port = port
        self._check_port_nums_from_defaults()

    def _check_port_nums_from_defaults(self):
        if (self._port == constants.UDP_CONNECTION_DEFAULT_PORT or
                self._port == constants.UDP_BOOT_CONNECTION_DEFAULT_PORT):
            raise exceptions.SpinnmanInvalidParameterException(
                "The port number speicified is one that is already used by "
                "either the boot or spinn api listener. therefore cannot be "
                "used as a port number to a iptag or reverse iptag")

