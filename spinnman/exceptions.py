# Copyright (c) 2017-2019 The University of Manchester
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import traceback


class SpinnmanException(Exception):
    """ Superclass of exceptions that occur when dealing with communication\
        with SpiNNaker
    """


class SpinnmanInvalidPacketException(SpinnmanException):
    """ An exception that indicates that a packet was not in the expected\
        format
    """

    def __init__(self, packet_type, problem):
        """
        :param str packet_type: The type of packet expected
        :param str problem: The problem with the packet
        """
        super().__init__("Invalid packet of type {} received: {}".format(
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
        :param str parameter: The name of the parameter that is invalid
        :param str value: The value of the parameter that is invalid
        :param str problem: The problem with the parameter
        """
        super().__init__(
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


class SpinnmanInvalidParameterTypeException(SpinnmanException):
    """ An exception that indicates that the type of one of the parameters\
        passed was invalid
    """

    def __init__(self, parameter, param_type, problem):
        """
        :param str parameter: The name of the parameter that is invalid
        :param str param_type: The type of the parameter that is invalid
        :param str problem: The problem with the parameter
        """
        super().__init__("Parameter {} of type {} is invalid: {}".format(
            parameter, param_type, problem))
        self._parameter = parameter
        self._type = param_type
        self._problem = problem

    @property
    def parameter(self):
        """ The parameter with an invalid value
        """
        return self._parameter

    @property
    def type(self):
        """ The value that is invalid
        """
        return self._type

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
        :param str problem: The problem with the IO
        """
        super().__init__("IO Error: {}".format(problem))
        self._problem = problem

    @property
    def problem(self):
        """ The problem with IO
        """
        return self._problem


class SpinnmanEOFException(SpinnmanIOException):
    """
    An exception that we're trying to do I/O on a closed socket.
    That isn't going to work!
    """

    def __init__(self):
        super().__init__("connection is closed")


class SpinnmanTimeoutException(SpinnmanException):
    """ An exception that indicates that a timeout occurred before an operation
        could finish
    """

    def __init__(self, operation, timeout, msg=None):
        """
        :param str operation: The operation being performed
        :param float timeout: The timeout value in seconds
        """
        if msg is None:
            msg = "Operation {} timed out after {} seconds".format(
                operation, timeout)
        super().__init__(msg)

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
        :param str operation: The operation being performed
        :param str command: The command being executed
        :param str response: The response received in error
        """
        super().__init__(
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


class SpinnmanGroupedProcessException(SpinnmanException):
    """ Encapsulates exceptions from processes which communicate with a\
        collection of cores/chips
    """
    def __init__(self, error_requests, exceptions, tracebacks, connections):
        problem = "Exceptions found were:\n"
        for error_request, exception, trace_back, connection in zip(
                error_requests, exceptions, tracebacks, connections):
            sdp_header = error_request.sdp_header
            phys_p = sdp_header.get_physical_cpu_id()
            location = "board {} with ethernet chip {}:{} [{}:{}:{}{}]".format(
                connection.remote_ip_address, connection.chip_x,
                connection.chip_y, sdp_header.destination_chip_x,
                sdp_header.destination_chip_y,
                sdp_header.destination_cpu, phys_p)
            problem += \
                "   Received exception class: {}\n" \
                "       With message {}\n" \
                "       When sending to {}\n" \
                "       Stack trace: {}\n".format(
                    exception.__class__.__name__, str(exception),
                    location,
                    traceback.format_tb(trace_back))
        super().__init__(problem)


class SpinnmanGenericProcessException(SpinnmanException):
    """ Encapsulates exceptions from processes which communicate with some\
        core/chip
    """
    def __init__(self, exception, tb, x, y, p, phys_p, tb2=None):
        """
        :param Exception exception:
        :param int x:
        :param int y:
        :param int p:
        :param str phys_p:
        """
        # pylint: disable=too-many-arguments
        super().__init__(
            "   Received exception class: {} \n"
            "      With message: {} \n"
            "      When sending to {}:{}:{}{}\n"
            "      Stack trace: {}\n".format(
                exception.__class__.__name__, str(exception), x, y, p,
                phys_p, traceback.format_tb(tb)))

        self._stored_exception = exception
        if tb2 is not None:
            self.__traceback__ = tb2

    @property
    def exception(self):
        """
        :rtype: Exception
        """
        return self._stored_exception


class SpinnmanUnsupportedOperationException(SpinnmanException):
    """ An exception that indicates that the given operation is not supported
    """

    def __init__(self, operation):
        """
        :param str operation: The operation being requested
        """
        super().__init__("Operation {} is not supported".format(operation))
        self._operation = operation

    @property
    def operation(self):
        """ The unsupported operation requested

        :rtype: str
        """
        return self._operation


class SpinnmanEIEIOPacketParsingException(SpinnmanException):
    """ Unable to complete the parsing of the EIEIO packet received.\
    The routine used is invalid or the content of the packet is invalid
    """

    def __init__(self, parsing_format, packet):
        """
        :param str parsing_format:
        :param bytes packet:
        """
        super().__init__(
            "The packet received is being parsed as an EIEIO {0:s} packet, "
            "but the content of the packet is invalid".format(parsing_format))
        self._packet = packet

    @property
    def packet(self):
        """
        :rtype: bytes
        """
        return self._packet


class SpiNNManCoresNotInStateException(SpinnmanTimeoutException):
    """ Cores failed to reach a given state within a timeout.
    """

    def __init__(self, timeout, expected_states, failed_core_states):
        """
        :param float timeout:
        :param set(CPUState) expected_states:
        :param CPUInfos failed_core_states:
        """
        n_cores = len(failed_core_states)
        if n_cores > 10:
            msg = "waiting for {} cores to reach one of {}".format(
                n_cores, expected_states)
        else:
            msg = "waiting for cores {} to reach one of {}".format(
                failed_core_states, expected_states)
        super().__init__(msg, timeout, msg)
        self._failed_core_states = failed_core_states

    def failed_core_states(self):
        """
        :rtype: CPUInfos
        """
        return self._failed_core_states


class SpallocException(SpinnmanException):
    """
    Raised when there is a problem with the Spalloc session or job
    """
