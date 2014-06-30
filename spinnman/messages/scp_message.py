from enum import Enum

from spinnman.messages.sdp_message import SDPMessage

class Command(Enum):
    """ The SCP Commands and Response codes
    """
    CMD_VER = (0, "Get SCAMP Version")
    CMD_RUN = 1
    CMD_READ = (2, "Read SDRAM")
    CMD_WRITE = (3, "Write SDRAM")
    CMD_APLX = 4
    CMD_FILL = 5
    CMD_REMAP = 16
    CMD_LINK_READ = (17, "Read chip link information")
    CMD_LINK_WRITE = 18
    CMD_AR = 19
    CMD_NNP = (20, "Send a Nearest-Neighbour packet")
    CMD_P2PC = 21
    CMD_SIG = (22, "Send a Signal")
    CMD_FFD = (23, "Send Flood-Fill Data")
    CMD_AS = 24
    CMD_LED = (25, "Control the LEDs")
    CMD_IPTAG = (26, "Set an IPTAG")
    CMD_SROM = 27
    CMD_FLASH_COPY = 49
    CMD_FLASH_ERASE = 50
    CMD_FLASH_WRITE = 51
    CMD_RESET = 55
    CMD_POWER = 57
    CMD_TUBE = 64
    RC_OK = (0x80, "Command completed OK")
    RC_LEN = (0x81, "Bad packet length")
    RC_SUM = (0x82, "Bad checksum")
    RC_CMD = (0x83, "Bad/invalid command")
    RC_ARG = (0x84, "Invalid arguments")
    RC_PORT = (0x85, "Bad port number")
    RC_TIMEOUT = (0x86, "Timeout")
    RC_ROUTE = (0x87, "No P2P route")
    RC_CPU = (0x88, "Bad CPU number")
    RC_DEAD = (0x89, "SHM destination dead")
    RC_BUF = (0x8a, "No free Shared Memory buffers")
    RC_P2P_NOREPLY = (0x8b, "No reply to open")
    RC_P2P_REJECT = (0x8c, "Open rejected")
    RC_P2P_BUSY = (0x8d, "Destination busy")
    RC_P2P_TIMEOUT = (0x8e, "Dest did not respond")
    RC_PKT_TX = (0x8f, "Pkt Transmission failed")
    
    def __init__(self, value, doc=""):
        self._value_ = value
        self.__doc__ = doc

class Signal(Enum):
    """ SCP Signals
    """
    INITIALISE = (0, 2)
    POWER_DOWN = (1, 2)
    STOP = (2, 2)
    START = (3, 2)
    SYNC0 = (4, 0)
    SYNC1 = (5, 0)
    PAUSE = (6, 0)
    CONTINUE = (7, 0)
    EXIT = (8, 2)
    TIMER = (9, 0)
    USER_0 = (10, 0)
    USER_1 = (11, 0)
    USER_2 = (12, 0)
    USER_3 = (13, 0)
    OR = (16, 1)
    AND = (17, 1)
    COUNT = (18, 1)
    
    def __init__(self, value, signal_type, doc=""):
        """
        
        :param value: The value used for the signal
        :type value: int
        :param signal_type: The "type" of the signal, between 0 and 2
        :type signal_type: int
        """
        self._value_ = value
        self._signal_type = signal_type
        self.__doc__ = doc
    
    @property
    def signal_type(self):
        return self._signal_type

class SCPMessage(SDPMessage):
    """ Wraps up an SCP Message inside an SDP Message
    """
    
    def __init__(self, flags, tag, destination_port, destination_chip_x, 
            destination_chip_y, destination_cpu, source_port,
            source_chip_x, source_chip_y, source_cpu, command, sequence, 
            argument_1, argument_2, argument_3, data):
        """
        :param flags: Any flags for the packet
        :type flags: :py:class:`spinnman.messages.sdp_message.Flag`
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
        :type command: :py:class:`Command`
        :param sequence: The number of the SCP packet in order of all packets\
                    sent or received, between 0 and 65535
        :type sequence: int
        :param argument_1: First argument of the SCP command
        :type argument_1: int
        :param argument_2: Second argument of the SCP command
        :type argument_2: int
        :param argument_3: Third argument of the SCP command
        :type argument_3: int
        :param data: The data of the SCP packet
        :type data: bytearray
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If one of\
                    the parameters is incorrect
        """
        pass
    
    @property
    def command(self):
        """ The command of the SCP packet
        
        :return: The command
        :rtype: Command
        """
        pass
    
    @property
    def sequence(self):
        """ The sequence number of the SCP packet
        
        :return: The sequence number of the packet, between 0 and 65535
        :rtype: int
        """
        pass
    
    @property
    def argument_1(self):
        """ The first argument of the SCP packet
        
        :return: The first argument of the packet
        :rtype: int
        """
        pass
    
    @property
    def argument_2(self):
        """ The second argument of the SCP packet
        
        :return: The second argument of the packet
        :rtype: int
        """
        pass
    
    @property
    def argument_3(self):
        """ The third argument of the SCP packet
        
        :return: The third argument of the packet
        :rtype: int
        """
        pass
