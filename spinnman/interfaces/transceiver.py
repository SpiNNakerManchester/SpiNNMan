__author__ = 'stokesa6'
from spinnman.interfaces.transceiver_tools.app_calls import _AppCalls
from spinnman.interfaces.transceiver_tools.iptag_calls import _IPTagCalls
from spinnman.interfaces.transceiver_tools.memory_calls import _MemoryCalls
from spinnman.interfaces.transceiver_tools.packet_calls import _PacketCalls
from spinnman.scp.scp_connection import _SCPConnection

class Transceiver(_AppCalls, _IPTagCalls, _MemoryCalls, _PacketCalls, object):
    """main transciever object, inherrits from multiple transciever tools to
       reduce the size of the transciever.
    """
    __all__ = ['_AppCalls', '_IPTagCalls', '_MemoryCalls', '_PacketCalls']

    def __init__(self, hostname, port=17893):
        """ constructor for a transciever object

        :param hostname: the hostname of the machine
        :param port: the port to which to listen for this machine
        :type hostname: str
        :type port: int
        :return: a new transceiver object
        :rtype: spinnman.interfaces.transceiver.Transceiver
        :raise None: does not raise any known exceptions
        """

        _AppCalls.__init__(self, self)
        _IPTagCalls.__init__(self, self)
        _MemoryCalls.__init__(self, self)
        _PacketCalls.__init__(self, self)

        self._x = 0
        self._y = 0
        self._cpu = 0
        self._node = (self._x << 8) | self._y
        self.utility = None
        self.conn = _SCPConnection(hostname, port)

    def load_targets(self, load_data_interface):
        """ public method for loading data targets to cores on a spinnaker\
            machine

        :param load_data_interface: an interface for retrieving data to load \
                                    for a core
        :type load_data_interface: diriritive of spinnman.interfaces.\
                                   load_interfaces.abstract_load_data_interface
        :return: None
        :rtype: None
        :raise spinnman.exceptions.SpinnmanSCPError: when there is error with\
                                                     the connection
        """
        pass

    def load_write_mem(self, load_data_interface):
        """ public method for loading memory writes to cores on a spinnaker\
            machine

        :param load_data_interface: an interface for retrieving data to load \
                                    for a core
        :type load_data_interface: diriritive of spinnman.interfaces.\
                                   load_interfaces.abstract_load_data_interface
        :return: None
        :rtype: None
        :raise spinnman.exceptions.SpinnmanSCPError: when there is error with \
                                                     the connection
        """
        pass

    def load_executables(self, load_executable_interface):
        """ public method for loading executable images to cores on a spinnaker\
            machine

        :param load_executable_interface: an interface for retrieving data \
                                          to load for a core
        :type load_executable_interface: diriritive of spinnman.interfaces.\
                                         load_interfaces.\
                                         abstract_load_executables_interface
        :return: None
        :rtype: None
        :raise spinnman.exceptions.SpinnmanSCPError: when there is error with
                                                     the connection
        """
        pass

    def check_synco(self, total_processors, app_id):
        """ public method that allows the end user to see if all the cores\
            associated with the given app_id are in sync0

        :param total_processors: The number of processors used in this \
                                 application
        :param app_id: the unique identifier for this application
        :type total_processors: int
        :type app_id: int
        :return: true or false given if all cores are in sync 0
        :rtype: boolean
        :raise None: does not raise any known exceptions
        """
        pass

    def run(self, app_id):
        """ public method that allows the end user set cores that are in sync0 \
            into the run state (executing)

        :param app_id: the unique identifier for this application
        :type app_id: int
        :return: None
        :rtype: None
        :raise spinnman.exceptions.SpinnmanSCPError: when there is error with \
                                                     the connection
        """
        pass

    def has_exited(self, app_id, total_processors):
        """ public method that allows the end user to see if all the cores\
            associated with the given app_id have exited

        :param total_processors: The number of processors used in this \
                                 application
        :param app_id: the unique identifier for this application
        :type total_processors: int
        :type app_id: int
        :return: true or false given if all cores are in sync 0
        :rtype: boolean
        :raise spinnman.exceptions.SpinnmanInvalidStateException:\
                    when some cores have resulted in crashed states \
                    (RTE, WDOG etc)
        """
        pass

    def get_iobuf(self, processor_coords):
        """ public method that allows the end user to read a collection of \
            memory that was reserved for iobuf prints.

        :param processor_coords: a tuple containing a processors x,y,p coords
        :type processor_coords: tuple containing x,y,p
        :return: a array of lines printed to iobuf
        :rtype: an iterable object containing strings
        :raise spinnman.exceptions.SpinnmanSCPError: when somethign fails at\
                            the connection level, such as timeouts etc.


        """
        pass
