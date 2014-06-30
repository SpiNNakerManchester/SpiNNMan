from enum import Enum

class State(Enum):
    """ SARK CPU States
    """
    DEAD = 0
    POWERED_DOWN = 1
    RUN_TIME_EXCEPTION = 2
    WATCHDOG = 3
    INITIALISING = 4
    READY = 5
    C_MAIN = 6
    RUNNING = 7
    SYNC0 = 8
    SYNC1 = 9
    PAUSED = 10
    FINSHED = 11
    IDLE = 15
    
    def __init__(self, value, doc=""):
        self._value_ = value
        self.__doc__ = doc
    
class RunTimeError(Enum):
    """ SARK Run time errors
    """
    NONE = 0
    RESET = 1
    UNDEF = 2
    SVC = 3 
    PABT = 4 
    DABT = 5 
    IRQ = 6
    FIQ = 7 
    VIC = 8 
    ABORT = 9
    MALLOC = 10
    DIVBY0 = 11
    EVENT = 12
    SWERR = 13
    IOBUF = 14
    
    def __init__(self, value, doc=""):
        self._value_ = value
        self.__doc__ = doc
    
class MailboxCommands(Enum):
    """ Commands sent between an application and the monitor processor
    """
    
    SHM_IDLE = (0, "The mailbox is idle")
    SHM_MSG = (1, "The mailbox contains an SDP message")
    SHM_NOP = (2, "The mailbox contains a non-operation")
    SHM_SIGNAL = (3, "The mailbox contains a signal")
    SHM_CMD = (4, "The mailbox contains a command")
    
    def __init__(self, value, doc=""):
        self._value_ = value
        self.__doc__ = doc

class CPUInfo(object):
    """ Represents information about the state of a CPU
    """
    
    def __init__(self, x, y, p, cpu_data):
        """
        :param cpu_data: An array of bytes received from SDRAM on the board
        :type cpu_data: bytearray
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If the\
                    array does not contain a cpu data structure
        """
        pass
    
    @property
    def x(self):
        """ The x-coordinate of the chip containing the core
        
        :return: The x-coordinate of the chip
        :rtype: int
        """
        pass
    
    @property
    def y(self):
        """ The y-coordinate of the chip containing the core
        
        :return: The y-coordinate of the chip
        :rtype: int
        """
        pass
    
    @property
    def p(self):
        """ The id of the core on the chip
        
        :return: The id of the core
        :rtype: int
        """
        pass
    
    @property
    def state(self):
        """ The current state of the core
        
        :return: The state of the core
        :rtype: State
        """
        pass
        
    @property
    def application_name(self):
        """ The name of the application running on the core
        
        :return: The name of the application
        :rtype: str
        """
        pass
    
    @property
    def application_id(self):
        """ The id of the application running on the core
        
        :return: The id of the application
        :rtype: int
        """
        pass
    
    @property
    def time(self):
        """ The time at which the application started
        
        :return: The time in seconds since 00:00:00 on the 1st January 1970
        :rtype: long
        """
        pass
    
    @property
    def run_time_error(self):
        """ The reason for a run time error
        
        :return: The run time error
        :rtype: RunTimeError
        """
        pass
    
    @property
    def application_mailbox_command(self):
        """ The command currently in the mailbox being sent from the monitor\
            processor to the application
        
        :return: The command
        :rtype: MailboxCommand
        """
        pass
    
    @property
    def application_mailbox_data_address(self):
        """ The address of the data in SDRAM for the application mailbox
        
        :return: The address of the data
        :rtype: int
        """
        pass
    
    @property
    def monitor_mailbox_command(self):
        """ The command currently in the mailbox being sent from the\
            application to the monitor processor
            
        :return: The command
        :rtype: MailboxCommand
        """
    
    @property
    def monitor_mailbox_data_address(self):
        """ The address of the data in SDRAM of the monitor mailbox
        
        :return: The address of the data
        :rtype: int
        """
        pass
    
    @property
    def software_error_count(self):
        """ The number of software errors counted
        
        :return: The number of software errors
        :rtype: int
        """
        pass
    
    @property
    def software_source_filename(self):
        """ The filename of the software source
        
        :return: The filename
        :rtype: str
        """
        pass
    
    @property
    def software_source_line_number(self):
        """ The line number of the software source
        
        :return: The line number
        :rtype: int
        """
        pass
    
    @property
    def processor_state_register(self):
        """ The value in the processor state register (psr)
        
        :return: The psr value
        :rtype: int
        """
        pass
    
    @property
    def stack_pointer(self):
        """ The current stack pointer value (sp)
        
        :return: The sp value
        :rtype: int
        """
        pass
    
    @property
    def link_register(self):
        """ The current link register value (lr)
        
        :return: The lr value
        :rtype: int
        """
        pass
    
    @property
    def registers(self):
        """ The current register values (r0 - r7)
        
        :return: An array of 8 values, one for each register
        :rtype: array of int
        """
        pass
    
    @property
    def user(self):
        """ The current user values (user0 - user3)
        
        :return: An array of 4 values, one for each user value
        :rtype: array of int
        """
        pass
    
    @property
    def iobuf_address(self):
        """ The address of the IOBUF buffer in SDRAM
        
        :return: The address
        :rtype: int
        """
        pass
