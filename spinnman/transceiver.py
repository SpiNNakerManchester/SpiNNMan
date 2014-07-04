def create_transceiver_from_hostname(cls, hostname):
    """ Create a Transceiver by creating a UDPConnection to the given\
        hostname on port 17893 (the default SCAMP port), discovering any\
        additional links using this connection, and then returning the\
        transceiver created with the conjunction of the created\
        UDPConnection and the discovered connections
    
    :param hostname: The hostname or IP address of the board
    :type hostname: str
    :return: The created transceiver
    :rtype: :py:class:`spinnman.transceiver.Transceiver`
    :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                communicating with the board
    :raise spinnman.exceptions.SpinnmanInvalidPacketException: If a packet\
                is received that is not in the valid format
    :raise spinnman.exceptions.SpinnmanInvalidParameterException: If a\
                packet is received that has invalid parameters
    :raise spinnman.exceptions.SpinnmanUnexpectedResponseCodeException: If\
                a response indicates an error during the exchange
    """
    pass

class Transceiver(object):
    """ An encapsulation of various communications with the spinnaker board
    """ 

    def __init__(self, connections):
        """

        :param connections: An iterable of connections to the board
        :type connections: An iterable of :py:class:`spinnman.connections.abstract_connection.AbstractConnection`
        :raise None: Does not raise any known exceptions
        """
        pass
    
    def discover_connections(self):
        """ Find connections to the board and store these for future use.\
            Note that connections can be empty, in which case another local\
            discovery mechanism will be used.  Note that an exception will be\
            thrown if no initial connections can be found to the board.
        
        :param scp_sender: A connection that can send SCP packets
        :type scp_sender: :py:class:`spinnman.connections.abstract_scp_sender.AbstractSCPSender`
        :param scp_receiver: A connection that can receive SCP packets
        :type scp_receiver: :py:class:`spinnman.connections.abstract_scp_receiver.AbstractSCPReceiver`
        :return: An iterable of discovered connections, not including the\
                    initially given connections in the constructor
        :rtype: iterable of :py:class:`spinnman.connections.abstract_connection.AbstractConnection`
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    communicating with the board
        :raise spinnman.exceptions.SpinnmanInvalidPacketException: If a packet\
                    is received that is not in the valid format
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If a\
                    packet is received that has invalid parameters
        :raise spinnman.exceptions.SpinnmanUnexpectedResponseCodeException: If\
                    a response indicates an error during the exchange
        """
        pass
    
    def get_connections(self):
        """ Get the currently known connections to the board, made up of those\
            passed in to the transceiver and those that are discovered during\
            calls to discover_connections.  No further discovery is done here.
        
        :return: An iterable of connections known to the transciever
        :rtype: iterable of :py:class:`spinnman.connections.abstract_connection.AbstractConnection`
        """
    
    def get_machine_dimensions(self):
        """ Get the maximum chip x-coordinate and maximum chip y-coordinate of\
            the chips in the machine
        
        :return: The dimensions of the machine
        :rtype: :py:class:`spinnman.model.machine_dimensions.MachineDimensions`
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    communicating with the board
        :raise spinnman.exceptions.SpinnmanInvalidPacketException: If a packet\
                    is received that is not in the valid format
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If a\
                    packet is received that has invalid parameters
        :raise spinnman.exceptions.SpinnmanUnexpectedResponseCodeException: If\
                    a response indicates an error during the exchange
        """
        pass
    
    def get_machine_details(self):
        """ Get the details of the machine made up of chips on a board and how\
            they are connected to each other.
            
        :return: A machine description
        :rtype: :py:class:`spinn_machine.machine.Machine`
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    communicating with the board
        :raise spinnman.exceptions.SpinnmanInvalidPacketException: If a packet\
                    is received that is not in the valid format
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If a\
                    packet is received that has invalid parameters
        :raise spinnman.exceptions.SpinnmanUnexpectedResponseCodeException: If\
                    a response indicates an error during the exchange
        """
    
    def get_detected_external_peripheral_links(self):
        """ Gets a list of links on which external peripherals are\
            detected to be connected to.  Note that if the external peripheral\
            does not communicate this information with the board, the\
            peripheral will not be listed here.\
            NOTE: This is EXPERIMENTAL and as such may change once a proper\
            protocol has been developed.
        
        :return: An iterable of links
        :rtype: An iterable of :py:class:`spinn_machine.link.Link`
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    communicating with the board
        :raise spinnman.exceptions.SpinnmanInvalidPacketException: If a packet\
                    is received that is not in the valid format
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If a\
                    packet is received that has invalid parameters
        :raise spinnman.exceptions.SpinnmanUnexpectedResponseCodeException: If\
                    a response indicates an error during the exchange
        """
        pass
    
    def is_connected(self, connection=None):
        """ Determines if the board can be contacted
        
        :param connection: The connection which is to be tested.  If none,\
                    all connections will be tested, and the board will be\
                    considered to be connected if any one connection works.
        :type connection: :py:class:`spinnman.connections.abstract_connection.AbstractConnection`
        :return: True if the board can be contacted, False otherwise
        :rtype: bool
        :raise None: No known exceptions are raised
        """
        pass
    
    def get_scamp_version(self, retries=3, timeout=1):
        """ Get the version of scamp which is running on the board
        
        :param retries: The number of times to retry getting the version
        :type retries: int
        :param timeout: The timeout for each retry in seconds
        :type timeout: int
        :return: The version identifier
        :rtype: :py:class:`spinnman.model.version_info.VersionInfo`
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    communicating with the board
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If the\
                    timeout is less than 1
        :raise spinnman.exceptions.SpinnmanTimeoutException: If none of the\
                    retries resulted in a response before the timeout\
                    (suggesting that the board is not booted)
        """
        pass
    
    def boot_board(self, board_version):
        """ Attempt to boot the board.  No check is performed to see if the\
            board is already booted.
        
        :param board_version: The version of the board e.g. 3 for a SpiNN-3\
                    board or 5 for a SpiNN-5 board.
        :type board_version: int
        :return: Nothing is returned
        :rtype: None
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    communicating with the board
        """
        pass
    
    def get_cpu_information(self, chips_and_cores=None):
        """ Get information about the processors on the board
        
        :param chips_and_cores: A set of chips and cores from which to get\
                    the information.  If not specified, the information from\
                    all of the cores on all of the chips on the board are\
                    obtained
        :type chips_and_cores: :py:class:`spinnman.model.chips_and_cores.ChipsAndCores`
        :return: An iterable of the cpu information for the selected cores, or\
                    all cores if chips_and_cores are not specified
        :rtype: iterable of :py:class:`spinnman.model.cpu_info.CPUInfo`
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    communicating with the board
        :raise spinnman.exceptions.SpinnmanInvalidPacketException: If a packet\
                    is received that is not in the valid format
        :raise spinnman.exceptions.SpinnmanInvalidParameterException:
                    * If chip_and_cores contains invalid items
                    * If a packet is received that has invalid parameters
        :raise spinnman.exceptions.SpinnmanUnexpectedResponseCodeException: If\
                    a response indicates an error during the exchange
        """
        pass
    
    def get_iobuf(self, chips_and_cores=None):
        """ Get the contents of the IOBUF buffer for a number of processors
        
        :param chips_and_cores: A set of chips and cores from which to get\
                    the buffers.  If not specified, the buffers from\
                    all of the cores on all of the chips on the board are\
                    obtained
        :type chips_and_cores: :py:class:`spinnman.model.chips_and_cores.ChipsAndCores`
        :return: An iterable of the buffers, which may not be in the order\
                    of chips_and_cores
        :rtype: iterable of :py:class:`spinnman.model.io_buffer.IOBuffer`
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    communicating with the board
        :raise spinnman.exceptions.SpinnmanInvalidPacketException: If a packet\
                    is received that is not in the valid format
        :raise spinnman.exceptions.SpinnmanInvalidParameterException:
                    * If chip_and_cores contains invalid items
                    * If a packet is received that has invalid parameters
        :raise spinnman.exceptions.SpinnmanUnexpectedResponseCodeException: If\
                    a response indicates an error during the exchange
        """
        pass
    
    def get_core_status_count(self, status, app_id=None):
        """ Get a count of the number of cores which have a given status
        
        :param status: The status count to get
        :type status: :py:class:`spinnman.model.cpu_info.State`
        :param app_id: The id of the application from which to get the count.\
                    If not specified, gets the count from all applications.
        :type app_id: int
        :return: A count of the cores with the given status
        :rtype: int
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    communicating with the board
        :raise spinnman.exceptions.SpinnmanInvalidPacketException: If a packet\
                    is received that is not in the valid format
        :raise spinnman.exceptions.SpinnmanInvalidParameterException:
                    * If status is not a valid status
                    * If app_id is not a valid application id
                    * If a packet is received that has invalid parameters
        :raise spinnman.exceptions.SpinnmanUnexpectedResponseCodeException: If\
                    a response indicates an error during the exchange
        """
        pass
    
    def execute(self, executable_data_items, app_id):
        """ Start a number of executables running on the board
        
        :param executable_data_items: An iterable of executable data items\
                     detailing what should be executed where
        :type executable_data_items: iterable of\
                    :py:class:`spinnman.data.abstract_executable_data_item.AbstractExecutableDataItem`
        :param app_id: The id of the application with which to associate the\
                    executables
        :type app_id: int
        :return: Nothing is returned
        :rtype: None
        :raise spinnman.exceptions.SpinnmanIOException:
                    * If there is an error communicating with the board
                    * If there is an error reading one of the executables
        :raise spinnman.exceptions.SpinnmanInvalidPacketException: If a packet\
                    is received that is not in the valid format
        :raise spinnman.exceptions.SpinnmanInvalidParameterException:
                    * If one of the items targets an invalid chip or core
                    * If a packet is received that has invalid parameters
        :raise spinnman.exceptions.SpinnmanUnexpectedResponseCodeException: If\
                    a response indicates an error during the exchange
        """
        pass
    
    def write_memory(self, load_data_items):
        """ Write to the SDRAM on the board
        
        :param load_data_items: An iterable of load data items detailing\
                    what should be written where
        :type load_data_items: iterable of\
                    :py:class:`spinnman.data.abstract_load_data_item.AbstractLoadDataItem`
        :return: Nothing is returned
        :rtype: None
        :raise spinnman.exceptions.SpinnmanIOException:
                    * If there is an error communicating with the board
                    * If there is an error reading the data
        :raise spinnman.exceptions.SpinnmanInvalidPacketException: If a packet\
                    is received that is not in the valid format
        :raise spinnman.exceptions.SpinnmanInvalidParameterException:
                    * If one of the items targets an invalid chip, core or\
                      base address
                    * If a packet is received that has invalid parameters
        :raise spinnman.exceptions.SpinnmanUnexpectedResponseCodeException: If\
                    a response indicates an error during the exchange
        """
        
    def read_memory(self, read_data_items):
        """ Read some areas of SDRAM from the board
        
        :param read_data_items: An iterable of read data items detailing what\
                    should be read from where and where to write it
        :type read_data_items: iterable of\
                    :py:class:`spinnman.data.abstract_read_data_item.AbstractReadDataItem`
        :return: Nothing is returned
        :rtype: None
        :raise spinnman.exceptions.SpinnmanIOException:
                    * If there is an error communicating with the board
                    * If there is an error writing the data
        :raise spinnman.exceptions.SpinnmanInvalidPacketException: If a packet\
                    is received that is not in the valid format
        :raise spinnman.exceptions.SpinnmanInvalidParameterException:
                    * If one of the items is to read from an invalid chip, core\
                      or base address
                    * If a packet is received that has invalid parameters
        :raise spinnman.exceptions.SpinnmanUnexpectedResponseCodeException: If\
                    a response indicates an error during the exchange
        """
        pass
    
    def send_signal(self, signal, app_id=None):
        """ Send a signal to an application
        
        :param signal: The signal to send
        :type signal: :py:class:`spinnman.messages.scp_message.Signal`
        :param app_id: The id of the application to send to.  If not specified,\
                    the signal is sent to all applications
        :type app_id: int
        :return: Nothing is returned
        :rtype: None
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    communicating with the board
        :raise spinnman.exceptions.SpinnmanInvalidPacketException: If a packet\
                    is received that is not in the valid format
        :raise spinnman.exceptions.SpinnmanInvalidParameterException:
                    * If signal is not a valid signal
                    * If app_id is not a valid application id
                    * If a packet is received that has invalid parameters
        :raise spinnman.exceptions.SpinnmanUnexpectedResponseCodeException: If\
                    a response indicates an error during the exchange
        """
        pass
    
    def set_ip_tag(self, ip_tag, connection=None):
        """ Set up an ip tag
        
        :param iptag: The iptag to set up
        :type iptag: :py:class:`spinnman.model.iptag.IPTag`
        :param connection: Connection where the tag should be set up.  If not\
                    specified, all SCPSender connections will send the message\
                    to set up the tag
        :type connection:\
                    :py:class:`spinnman.connections.abstract_scp_sender.AbstractSCPSender`
        :return: Nothing is returned
        :rtype: None
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    communicating with the board
        :raise spinnman.exceptions.SpinnmanInvalidPacketException: If a packet\
                    is received that is not in the valid format
        :raise spinnman.exceptions.SpinnmanInvalidParameterException:
                    * If the ip tag fields are incorrect
                    * If the connection cannot send SDP messages
                    * If a packet is received that has invalid parameters
        :raise spinnman.exceptions.SpinnmanUnexpectedResponseCodeException: If\
                    a response indicates an error during the exchange
        """
        pass
    
    def clear_ip_tag(self, tag, connection=None):
        """ Clear the setting of an ip tag
        
        :param tag: The tag id
        :type tag: int
        :param connection: Connection where the tag should be cleard.  If not\
                    specified, all SCPSender connections will send the message\
                    to clear the tag
        :type connection:\
                    :py:class:`spinnman.connections.abstract_scp_sender.AbstractSCPSender`
        :return: Nothing is returned
        :rtype: None
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    communicating with the board
        :raise spinnman.exceptions.SpinnmanInvalidPacketException: If a packet\
                    is received that is not in the valid format
        :raise spinnman.exceptions.SpinnmanInvalidParameterException:
                    * If the tag is not a valid tag
                    * If the connection cannot send SDP messages
                    * If a packet is received that has invalid parameters
        :raise spinnman.exceptions.SpinnmanUnexpectedResponseCodeException: If\
                    a response indicates an error during the exchange
        """
        pass
    
    def get_ip_tags(self, connection=None):
        """ Get the current set of ip tags that have been set on the board
        
        :param connection: Connection from which the tags should be received.\
                    If not specified, all SCPSender connections will be queried\
                    and the response will be combined.
        :type connection:\
                    :py:class:`spinnman.connections.abstract_scp_sender.AbstractSCPSender`
        :return: An iterable of ip tags
        :rtype: iterable of :py:class:`spinnman.model.iptag.IPTag`
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    communicating with the board
        :raise spinnman.exceptions.SpinnmanInvalidPacketException: If a packet\
                    is received that is not in the valid format
        :raise spinnman.exceptions.SpinnmanInvalidParameterException:
                    * If the connection cannot send SDP messages
                    * If a packet is received that has invalid parameters
        :raise spinnman.exceptions.SpinnmanUnexpectedResponseCodeException: If\
                    a response indicates an error during the exchange
        """
        pass
    
    def load_multicast_routes(self, app_id, x, y, routes):
        """ Load a set of multicast routes on to a chip
        
        :param app_id: The id of the application to associate routes with
        :type app_id: int
        :param x: The x-coordinate of the chip onto which to load the routes
        :type x: int
        :param y: The y-coordinate of the chip onto which to load the routes
        :type y: int
        :param route_data_item: An iterable of multicast routes to load
        :type route_data_item: iterable of\
                    :py:class:`spinnman.model.multicast_routing_entry.MulticastRoute`
        :return: Nothing is returned
        :rtype: None
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    communicating with the board
        :raise spinnman.exceptions.SpinnmanInvalidPacketException: If a packet\
                    is received that is not in the valid format
        :raise spinnman.exceptions.SpinnmanInvalidParameterException:
                    * If any of the routes are invalid
                    * If a packet is received that has invalid parameters
        :raise spinnman.exceptions.SpinnmanUnexpectedResponseCodeException: If\
                    a response indicates an error during the exchange
        """
        pass
    
    def get_multicast_routes(self, x, y, app_id=None):
        """ Get the current multicast routes set up on a chip
        
        :param x: The x-coordinate of the chip from which to get the routes
        :type x: int
        :param y: The y-coordinate of the chip from which to get the routes
        :type y: int
        :param app_id: Optional application id of the routes.  If not specified\
                    all the routes will be returned.  If specified, the routes\
                    will be filtered so that only those for the given\
                    application are returned.
        :type app_id: int
        :return: An iterable of multicast routes
        :rtype: iterable of :py:class:`spinnman.model.multicast_routing_entry.MulticastRoute`
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    communicating with the board
        :raise spinnman.exceptions.SpinnmanInvalidPacketException: If a packet\
                    is received that is not in the valid format
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If a\
                    packet is received that has invalid parameters
        :raise spinnman.exceptions.SpinnmanUnexpectedResponseCodeException: If\
                    a response indicates an error during the exchange
        """
        pass
    
    def clear_multicast_routes(self, x, y, app_id=None):
        """ Remove all the multicast routes on a chip
        :param x: The x-coordinate of the chip on which to clear the routes
        :type x: int
        :param y: The y-coordinate of the chip on which to clear the routes
        :type y: int
        :param app_id: Optional application id of the routes.  If not specified\
                    all the routes will be cleared.  If specified, only the\
                    routes with the given application id will be removed.
        :return: Nothing is returned
        :rtype: None
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    communicating with the board
        :raise spinnman.exceptions.SpinnmanInvalidPacketException: If a packet\
                    is received that is not in the valid format
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If a\
                    packet is received that has invalid parameters
        :raise spinnman.exceptions.SpinnmanUnexpectedResponseCodeException: If\
                    a response indicates an error during the exchange
        """
        pass
    
    def get_router_diagnostics(self, x, y):
        """ Get router diagnostic information from a chip
        
        :param x: The x-coordinate of the chip from which to get the information
        :type x: int
        :param y: The y-coordinate of the chip from which to get the information
        :type y: int
        :return: The router diagnostic information
        :rtype: :py:class:`spinnman.model.router_diagnostics.RouterDiagnostics`
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    communicating with the board
        :raise spinnman.exceptions.SpinnmanInvalidPacketException: If a packet\
                    is received that is not in the valid format
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If a\
                    packet is received that has invalid parameters
        :raise spinnman.exceptions.SpinnmanUnexpectedResponseCodeException: If\
                    a response indicates an error during the exchange
        """
        pass
    
    def send_multicast(self, x, y, multicast_message, connection=None):
        """ Sends a multicast message to the board
        
        :param x: The x-coordinate of the chip where the message should first\
                    arrive on the board
        :type x: int
        :param y: The y-coordinate of the chip where the message should first\
                    arrive on the board
        :type y: int
        :param multicast_message: A multicast message to send
        :type multicast_message:\
                    :py:class:`spinnman.messages.multicast_message.MulticastMessage`
        :param connection: A specific connection over which to send the\
                    message.  If not specified, an appropriate connection is\
                    chosen automatically
        :type connection:\
                    :py:class:`spinnman.connections.abstract_multicast_sender.AbstractMulticastSender`
        :return: Nothing is returned
        :rtype: None
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    communicating with the board
        :raise spinnman.exceptions.SpinnmanUnsupportedOperationException: 
                    * If there is no connection that supports sending over\
                      multicast (or the given connection does not)
                    * If there is no connection that can make the packet\
                      arrive at the selected chip (ignoring routing tables)
        """
        pass
    
    def receive_multicast(self, x, y, timeout=None, connection=None):
        """ Receives a multicast message from the board
        
        :param x: The x-coordinate of the chip where the message should come\
                    from on the board
        :type x: int
        :param y: The y-coordinate of the chip where the message should come\
                    from on the board
        :type y: int
        :param timeout: Amount of time to wait for the message to arrive in\
                    seconds before a timeout.  If not specified, will wait\
                    indefinitely, or until the selected connection is closed
        :type timeout: int
        :param connection: A specific connection from which to receive the\
                    message.  If not specified, an appropriate connection is\
                    chosen automatically
        :type connection:\
                    :py:class:`spinnman.connections.abstract_multicast_receiver.AbstractMulticastReceiver`
        :return: The received message
        :rtype: :py:class:`spinnman.messages.multicast_message.MulticastMessage`
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    communicating with the board
        :raise spinnman.exceptions.SpinnmanUnsupportedOperationException: 
                    * If there is no connection that supports reception over\
                      multicast (or the given connection does not)
                    * If there is no connection that can receive a packet\
                      from the selected chip (ignoring routing tables)
        :raise spinnman.exceptions.SpinnmanInvalidPacketException: If the\
                    message received is not a valid multicast message
        :raise spinnman.exceptions.SpinnmanInvalidParameterException:
                    * If the timeout value is not valid
                    * If the received packet has an invalid parameter
        """
        pass
    
    def send_sdp_message(self, sdp_message, connection=None):
        """ Sends an SDP message to the board
        
        :param sdp_message: The SDP message to send
        :type sdp_message: :py:class:`spinnman.messages.sdp_message.SDPMessage`
        :param connection: A specific connection over which to send the\
                    message.  If not specified, an appropriate connection is\
                    chosen automatically
        :type connection:\
                    :py:class:`spinnman.connections.abstract_sdp_sender.AbstractSDPSender`
        :return: Nothing is returned
        :rtype: None
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    communicating with the board
        :raise spinnman.exceptions.SpinnmanUnsupportedOperationException: If\
                    there is no connection that supports sending SDP\
                    messages (or the given connection does not)
        """
        pass
    
    def receive_sdp_message(self, timeout=None, connection=None):
        """ Receives an SDP message from the board
        
        :param timeout: Amount of time to wait for the message to arrive in\
                    seconds before a timeout.  If not specified, will wait\
                    indefinitely, or until the selected connection is closed
        :type timeout: int
        :param connection: A specific connection from which to receive the\
                    message.  If not specified, an appropriate connection is\
                    chosen automatically
        :type connection:\
                    :py:class:`spinnman.connections.abstract_sdp_receiver.AbstractSDPReceiver`
        :return: The received message
        :rtype: :py:class:`spinnman.messages.sdp_message.SDPMessage`
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    communicating with the board
        :raise spinnman.exceptions.SpinnmanUnsupportedOperationException: If\
                    there is no connection that supports reception of\
                    SDP (or the given connection does not)
        :raise spinnman.exceptions.SpinnmanInvalidPacketException: If the\
                    message received is not a valid SDP message
        :raise spinnman.exceptions.SpinnmanInvalidParameterException:
                    * If the timeout value is not valid
                    * If the received packet has an invalid parameter
        """
        pass
    
    def send_scp_message(self, scp_message, connection=None):
        """ Sends an SCP message to the board
        
        :param scp_message: The SDP message to send
        :type scp_message: :py:class:`spinnman.messages.scp_message.SCPMessage`
        :param connection: A specific connection over which to send the\
                    message.  If not specified, an appropriate connection is\
                    chosen automatically
        :type connection:\
                    :py:class:`spinnman.connections.abstract_scp_sender.AbstractSCPSender`
        :return: Nothing is returned
        :rtype: None
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    communicating with the board
        :raise spinnman.exceptions.SpinnmanUnsupportedOperationException: If\
                    there is no connection that supports sending SCP\
                    messages (or the given connection does not)
        """
        pass
    
    def receive_scp_message(self, timeout=None, connection=None):
        """ Receives an SCP message from the board
        
        :param timeout: Amount of time to wait for the message to arrive in\
                    seconds before a timeout.  If not specified, will wait\
                    indefinitely, or until the selected connection is closed
        :type timeout: int
        :param connection: A specific connection from which to receive the\
                    message.  If not specified, an appropriate connection is\
                    chosen automatically
        :type connection:\
                    :py:class:`spinnman.connections.abstract_scp_receiver.AbstractSCPReceiver`
        :return: The received message
        :rtype: :py:class:`spinnman.messages.scp_message.SCPMessage`
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    communicating with the board
        :raise spinnman.exceptions.SpinnmanUnsupportedOperationException: If\
                    there is no connection that supports reception of\
                    SCP (or the given connection does not)
        :raise spinnman.exceptions.SpinnmanInvalidPacketException: If the\
                    message received is not a valid SCP message
        :raise spinnman.exceptions.SpinnmanInvalidParameterException:
                    * If the timeout value is not valid
                    * If the received packet has an invalid parameter
        """
        pass
