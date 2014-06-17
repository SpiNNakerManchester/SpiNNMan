__author__ = 'stokesa6'
from spinnman.interfaces.transceiver_tools.app_calls import AppCalls
from spinnman.interfaces.transceiver_tools.iptag_calls import IPTagCalls
from spinnman.interfaces.transceiver_tools.memory_calls import MemoryCalls
from spinnman.interfaces.transceiver_tools.packet_calls import PacketCalls
from spinnman.scp.scp_connection import SCPConnection

class Transceiver(AppCalls, IPTagCalls, MemoryCalls, PacketCalls, object):
    """main transciever object, inherrits from multiple transciever tools to
       reduce the size of the transciever.
    """

    def __init__(self, hostname, port=17893):
        """ constructor for a transciever object

        :param hostname: the hostname of the machine
        :param port: the port to which to listen for this machine
        :type hostname: str
        :type port: int
        :return a new transceiver object
        :rtype: spinnman.interfaces.transceiver.Transciever
        :raise None: does not raise any known exceptions
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
        self.conn = SCPConnection(hostname, port)

    def load_targets(self, load_data):
        pass

    def load_targets_raw(self, targets):
        pass

    def load_targets_load(self, file_name):
        pass

    def load_write_mem(self, load_data):
        pass

    def load_write_mem_raw(self, targets):
        pass

    def load_write_mem_load(self, file_name):
        pass

    def run(self, app_id):
        pass

    def run_raw(self, targets, run_time, app_id, iptags):
        pass

    def _check_synco_and_run(self, total_processors, app_id, run_time):
        pass

    def select(self, *args):
        pass
