
class SpinnmanException(Exception):
    """ Superclass of exceptions that occur when dealing with communication with
        SpiNNaker
    """
    pass
    
class SpinnmanInvalidPacketException(SpinnmanException):
    """ An exception that indicates that a packet was not in the expected format
    """
    
    def __init__(self, packet_type, problem):
        """
        :param packet_type: The type of packet expected
        :type packet_type: str
        :param problem: The problem with the packet
        :type problem: str
        """
        pass
    
class SpinnmanInvalidParameterException(SpinnmanException):
    """ An exception that indicates that the value of one of the parameters\
        passed was invalid
    """
    
    def __init__(self, parameter, value, problem):
        """
        :param parameter: The name of the parameter that is invalid
        :type parameter: str
        :param value: The value of the parameter that is invalid
        :type value: str
        :param problem: The problem with the parameter
        :type problem: str
        """
        pass
    
class SpinnmanIOException(SpinnmanException):
    """ An exception that something went wrong with the underlying IO
    """
    
    def __init__(self, problem):
        """
        :param problem: The problem with the IO
        :type problem: str
        """
        pass

class SpinnmanTimeoutException(SpinnmanException):
    """ An exception that indicates that a timeout occurred before an operation
        could finish
    """
    
    def __init__(self, operation, timeout):
        """
        :param operation: The operation being performed
        :type operation: str
        :param timeout: The timeout value in seconds
        :type timeout: int
        """
        pass

class SpinnmanUnexpectedResponseCodeException(SpinnmanException):
    """ Indicate that a response code returned from the board was unexpected\
        for the current operation
    """
    
    def __init__(self, operation, command, response):
        """
        :param operation: The operation being performed
        :type operation: str
        :param command: The command being executed
        :type command: str
        :param response: The response received in error
        :type response: str
        """
        pass

class SpinnmanUnsupportedOperationException(SpinnmanException):
    """ An exception that indicates that the given operation is not supported
    """
    
    def __init__(self, operation):
        """ 
        :param operation: The operation being requested
        :type operation: str
        """
        pass
