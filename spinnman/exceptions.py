
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
        super(SpinnmanInvalidPacketException, self).__init__(
                "Invalid packet of type {} received: {}".format(
                        packet_type, problem))
        self._packet_type = packet_type
        self._problem = problem
        
    @property
    def packet_type(self):
        """ The packet type
        """
        return self._packet_type
    
    @property
    def problem(self):
        """ The problem with the packet
        """
        return self._problem
    
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
        super(SpinnmanInvalidParameterException, self).__init__(
                "Setting parameter {} to value {} is invalid: {}".format(
                        parameter, value, problem))
        self._parameter = parameter
        self._value = value
        self._problem = problem
        
    @property
    def parameter(self):
        """ The parameter with an invalid value
        """
        return self._parameter
    
    @property
    def value(self):
        """ The value that is invalid
        """
        return self._value
    
    @property
    def problem(self):
        """ The problem with the parameter value
        """
        return self._problem

    
class SpinnmanIOException(SpinnmanException):
    """ An exception that something went wrong with the underlying IO
    """
    
    def __init__(self, problem):
        """
        :param problem: The problem with the IO
        :type problem: str
        """
        super(SpinnmanIOException, self).__init__("IO Error: {}".format(
                problem))
        self._problem = problem
    
    @property
    def problem(self):
        """ The problem with IO
        """
        return self._problem


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
        super(SpinnmanTimeoutException, self).__init__(
                "Operation {} timed out after {} seconds".format(
                        operation, timeout))
        
        self._operation = operation
        self._timeout = timeout
        
    @property
    def operation(self):
        """ The operation that was performed
        """
        return self._operation
    
    @property
    def timeout(self):
        """ The timeout value in seconds
        """
        return self._timeout


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
        super(SpinnmanUnexpectedResponseCodeException, self).__init__(
                "Unexpected response {} while performing operation {} using"
                " command {}".format(response, operation, command))
        self._operation = operation
        self._command = command
        self._response = response
        
    @property
    def operation(self):
        """ The operation being performed
        """
        return self._operation
    
    @property
    def command(self):
        """ The command being executed
        """
        return self._command
    
    @property
    def response(self):
        """ The unexpected response
        """
        return self._response


class SpinnmanUnsupportedOperationException(SpinnmanException):
    """ An exception that indicates that the given operation is not supported
    """
    
    def __init__(self, operation):
        """ 
        :param operation: The operation being requested
        :type operation: str
        """
        super(SpinnmanUnsupportedOperationException, self).__init__(
                "Operation {} is not supported".format(operation))
        self._operation = operation
    
    @property
    def operation(self):
        """ The unsupported operation requested
        """
        return self._operation
