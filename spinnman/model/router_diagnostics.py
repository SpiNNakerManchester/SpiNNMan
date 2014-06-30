class RouterDiagnostics(object):
    """ Represents a set of diagnostic information available from a chip router
    """
    
    def __init__(self, control_register, error_status, register_values):
        """
        :param control_register: The value of the control register
        :type control_register: int
        :param error_status: The value of the error_status
        :type error_status: int
        :param register_values: The values of the 16 router registers
        :type register_values: iterable of int
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If the\
                    number of register values is not 16
        """
        pass
    
    @property
    def mon(self):
        """ The "mon" part of the control register
        
        :return: The mon bits
        :rtype: int
        """
        pass
    
    @property
    def wait_1(self):
        """ The wait_1 part of the control register
        
        :return: The wait_1 bits
        :rtype: int
        """
        pass
        
    @property
    def wait_2(self):
        """ The wait_2 part of the control register
        
        :return: The wait_2 bits
        :rtype: int
        """
        pass
    
    @property
    def error_status(self):
        """ The error status
        
        :return: The error status
        :rtype: int
        """
        pass
    
    @property
    def n_local_multicast_packets(self):
        """ The number of multicast packets received from local cores
        
        :return: The number of packets
        :rtype: int
        """
        pass
    
    @property
    def n_external_multicast_packets(self):
        """ The number of multicast packets received from external links
        
        :return: The number of packets
        :rtype: int
        """
        pass
    
    @property
    def n_dropped_multicast_packets(self):
        """ The number of multicast packets received that were dropped
        
        :return: The number of packets
        :rtype: int
        """
        pass
    
    @property
    def n_local_peer_to_peer_packets(self):
        """ The number of peer-to-peer packets received from local cores
        
        :return: The number of packets
        :rtype: int
        """
        pass
    
    @property
    def n_external_peer_to_peer_packets(self):
        """ The number of peer-to-peer packets received from external links
        
        :return: The number of packets
        :rtype: int
        """
        pass
    
    @property
    def n_dropped_peer_to_peer_packets(self):
        """ The number of peer-to-peer packets received that were dropped
        
        :return: The number of packets
        :rtype: int
        """
        pass

    @property
    def n_local_nearest_neighbour_packets(self):
        """ The number of nearest-neighbour packets received from local cores
        
        :return: The number of packets
        :rtype: int
        """
        pass
    
    @property
    def n_external_nearest_neighbour_packets(self):
        """ The number of nearest-neighbour packets received from external links
        
        :return: The number of packets
        :rtype: int
        """
        pass
    
    @property
    def n_dropped_nearest_neighbour_packets(self):
        """ The number of nearest-neighbour packets received that were dropped
        
        :return: The number of packets
        :rtype: int
        """
        pass
    
    @property
    def n_local_fixed_route_packets(self):
        """ The number of fixed-route packets received from local cores
        
        :return: The number of packets
        :rtype: int
        """
        pass
    
    @property
    def n_external_fixed_route_packets(self):
        """ The number of fixed-route packets received from external links
        
        :return: The number of packets
        :rtype: int
        """
        pass
    
    @property
    def n_dropped_fixed_route_packets(self):
        """ The number of fixed-route packets received that were dropped
        
        :return: The number of packets
        :rtype: int
        """
        pass
    
    @property
    def user_registers(self):
        """ The values in the user control registers
        
        :return: An array of 4 values
        :rtype: array of int
        """
        pass
