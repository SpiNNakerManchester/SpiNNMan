__author__ = 'stokesa6'
from spinnman.interfaces.transceiver_tools.app_calls import AppCalls
from spinnman.interfaces.transceiver_tools.iptag_calls import IPTagCalls
from spinnman.interfaces.transceiver_tools.memory_calls import MemoryCalls
from spinnman.interfaces.transceiver_tools.packet_calls import PacketCalls

class Transceiver(AppCalls, IPTagCalls, MemoryCalls, PacketCalls, object):
    """main transciever object, inherrits from multiple transciever tools to
       reduce the size of the transciever.
    """

    def __init__(self, hostname, port=17893):
        """

        """
        AppCalls.__init__(self, self)
        IPTagCalls.__init__(self, self)
        MemoryCalls.__init__(self, self)
        PacketCalls.__init__(self, self)

        self._x = 0
        self._y = 0
        self._cpu = 0
        self._node = (self._x << 8) | self._y
        self.utility = None