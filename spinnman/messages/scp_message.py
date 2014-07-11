from spinnman.messages.sdp_message import SDPMessage
from spinnman.exceptions import SpinnmanInvalidParameterException


class SCPMessage(SDPMessage):
    """ Wraps up an SCP Message inside an SDP Message.  The sequence number can\
        be set once, either in the constructor or via the setter.  An exception\
        will occur if an attempt is made to set it more than once.
    """
    
    def __init__(self, flags, destination_port, destination_chip_x, 
            destination_chip_y, destination_cpu, command, argument_1, 
            argument_2, argument_3, sequence=None, tag=None, source_port=None,
            source_chip_x=None, source_chip_y=None, source_cpu=None, 
            data=None):
        """
        :param flags: Any flags for the packet
        :type flags: :py:class:`spinnman.messages.sdp_flag.SDPFlag`
        :param tag: The ip tag of the packet between 0 and 255
        :type tag: int
        :param destination_port: The destination port of the packet between 1\
                    and 7
        :type destination_port: int
        :param destination_chip_x: The x-coordinate of the destination chip\
                    between 0 and 255
        :type destination_chip_x: int
        :param destination_chip_y: The y-coordinate of the destination chip\
                    between 0 and 255
        :type destination_chip_y: int
        :param destination_cpu: The destination processor id within the chip\
                    between 0 and 31
        :type destination_cpu: int
        :param source_port: The source port of the packet between 1 and 7
        :type source_port: int
        :param source_chip_x: The x-coordinate of the source chip\
                    between 0 and 255
        :type source_chip_x: int
        :param source_chip_y: The y-coordinate of the source chip\
                    between 0 and 255
        :param source_cpu: The source processor id within the chip\
                   between 0 and 31
        :type source_cpu: int
        :param command: The SCP command
        :type command: :py:class:`spinnman.messages.scp_command.SCPCommand`
        :param sequence: The number of the SCP packet in order of all packets\
                    sent or received, between 0 and 65535
        :type sequence: int
        :param argument_1: First argument of the SCP command
        :type argument_1: int
        :param argument_2: Second argument of the SCP command
        :type argument_2: int
        :param argument_3: Third argument of the SCP command
        :type argument_3: int
        :param data: The data of the SCP packet, up to 256 bytes
        :type data: bytearray
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If one of\
                    the parameters is incorrect
        """
        
        if data is not None and len(data) > 256:
            raise SpinnmanInvalidParameterException(
                    "len(data)", str(len(data)), 
                    "The length of the data cannot exceed 256 bytes")
        
        super(SCPMessage, self).__init__(
                flags=flags, tag=tag, destination_port=destination_port, 
                destination_chip_x=destination_chip_x, 
                destination_chip_y=destination_chip_y, 
                destination_cpu=destination_cpu, source_port=source_port, 
                source_chip_x=source_chip_x, source_chip_y=source_chip_y, 
                source_cpu=source_cpu, data=data)
        self._command = command
        self._sequence = None
        self._argument_1 = argument_1
        self._argument_2 = argument_2
        self._argument_3 = argument_3
        
        self.sequence = sequence
    
    @property
    def command(self):
        """ The command of the SCP packet
        
        :return: The command
        :rtype: :py:class:`spinnman.messages.scp_command.SCPCommand`
        """
        return self._command
    
    @property
    def sequence(self):
        """ The sequence number of the SCP packet
        
        :return: The sequence number of the packet, between 0 and 65535
        :rtype: int
        """
        return self._sequence
    
    @sequence.setter
    def sequence(self, sequence):
        """ Set the sequence number of the SCP packet
        
        :param sequence: The sequence number to set, between 0 and 65535
        :type sequence: int
        :return: Nothing is returned
        :rtype: None
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If the\
                    sequence is out of range, or if it has already been set
        """
        if self._sequence is not None:
            raise SpinnmanInvalidParameterException(
                    "sequence", str(sequence),
                    "The sequence has already been set")
        if sequence is not None and (sequence < 0 or sequence > 65535):
            raise SpinnmanInvalidParameterException(
                    "sequence", str(sequence),
                    "The sequence must be between 0 and 65535")
        self._sequence = sequence
    
    @property
    def argument_1(self):
        """ The first argument of the SCP packet
        
        :return: The first argument of the packet
        :rtype: int
        """
        return self._argument_1
    
    @property
    def argument_2(self):
        """ The second argument of the SCP packet
        
        :return: The second argument of the packet
        :rtype: int
        """
        return self._argument_2
    
    @property
    def argument_3(self):
        """ The third argument of the SCP packet
        
        :return: The third argument of the packet
        :rtype: int
        """
        return self._argument_3
    
    @property
    def data(self):
        """ The data of the SCP packet
        
        :return: The data
        :rtype: bytearray
        """
        return super(SCPMessage, self).data
