# Copyright (c) 2014 The University of Manchester
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import traceback


class SpinnmanException(Exception):
    """
    Superclass of exceptions that occur when dealing with communication
    with SpiNNaker.
    """


class SpinnmanInvalidPacketException(SpinnmanException):
    """
    An exception that indicates that a packet was not in the expected format.
    """

    def __init__(self, packet_type, problem):
        """
        :param str packet_type: The type of packet expected
        :param str problem: The problem with the packet
        """
        super().__init__(
            f"Invalid packet of type {packet_type} received: {problem}")
        self._packet_type = packet_type
        self._problem = problem

    @property
    def packet_type(self):
        """
        The packet type.

        :rtype: str
        """
        return self._packet_type

    @property
    def problem(self):
        """
        The problem with the packet.

        :rtype: str
        """
        return self._problem


class SpinnmanInvalidParameterException(SpinnmanException):
    """
    An exception that indicates that the value of one of the parameters
    passed was invalid.
    """

    def __init__(self, parameter, value, problem):
        """
        :param str parameter: The name of the parameter that is invalid
        :param str value: The value of the parameter that is invalid
        :param str problem: The problem with the parameter
        """
        super().__init__(
            f"Setting parameter {parameter} to value {value} is invalid: "
            f"{problem}")
        self._parameter = parameter
        self._value = value
        self._problem = problem

    @property
    def parameter(self):
        """
        The parameter with an invalid value.

        :rtype: str
        """
        return self._parameter

    @property
    def value(self):
        """
        The value that is invalid.
        """
        return self._value

    @property
    def problem(self):
        """
        The problem with the parameter value.

        :rtype: str
        """
        return self._problem


class SpinnmanInvalidParameterTypeException(SpinnmanException):
    """
    An exception that indicates that the type of one of the parameters
    passed was invalid.
    """

    def __init__(self, parameter, param_type, problem):
        """
        :param str parameter: The name of the parameter that is invalid
        :param str param_type: The type of the parameter that is invalid
        :param str problem: The problem with the parameter
        """
        super().__init__(
            f"Parameter {parameter} of type {param_type} is invalid: "
            f"{problem}")
        self._parameter = parameter
        self._type = param_type
        self._problem = problem

    @property
    def parameter(self):
        """
        The parameter with an invalid value.

        :rtype: str
        """
        return self._parameter

    @property
    def type(self):
        """
        The value that is invalid.
        """
        return self._type

    @property
    def problem(self):
        """
        The problem with the parameter value.

        :rtype: str
        """
        return self._problem


class SpinnmanIOException(SpinnmanException):
    """
    An exception that something went wrong with the underlying IO.
    """

    def __init__(self, problem):
        """
        :param str problem: The problem with the IO
        """
        super().__init__(f"IO Error: {problem}")
        self._problem = problem

    @property
    def problem(self):
        """
        The problem with IO.

        :rtype: str
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
    """
    An exception that indicates that a timeout occurred before an operation
    could finish.
    """

    def __init__(self, operation, timeout, msg=None):
        """
        :param str operation: The operation being performed
        :param float timeout: The timeout value in seconds
        """
        if msg is None:
            msg = f"Operation {operation} timed out after {timeout} seconds"
        super().__init__(msg)

        self._operation = operation
        self._timeout = timeout

    @property
    def operation(self):
        """
        The operation that was performed.

        :rtype: str
        """
        return self._operation

    @property
    def timeout(self):
        """
        The timeout value in seconds.

        :rtype: float
        """
        return self._timeout


class SpinnmanUnexpectedResponseCodeException(SpinnmanException):
    """
    Indicate that a response code returned from the board was unexpected
    for the current operation.
    """

    def __init__(self, operation, command, response):
        """
        :param str operation: The operation being performed
        :param str command: The command being executed
        :param str response: The response received in error
        """
        super().__init__(
            f"Unexpected response {response} while performing "
            f"operation {operation} using command {command}")
        self._operation = operation
        self._command = command
        self._response = response

    @property
    def operation(self):
        """
        The operation being performed.

        :rtype: str
        """
        return self._operation

    @property
    def command(self):
        """
        The command being executed.
        """
        return self._command

    @property
    def response(self):
        """
        The unexpected response.

        :rtype: str
        """
        return self._response


class SpinnmanGroupedProcessException(SpinnmanException):
    """
    Encapsulates exceptions from processes which communicate with a
    collection of cores/chips.
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
    """
    Encapsulates exceptions from processes which communicate with some
    core/chip.
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
    """
    An exception that indicates that the given operation is not supported.
    """

    def __init__(self, operation):
        """
        :param str operation: The operation being requested
        """
        super().__init__(f"Operation {operation} is not supported")
        self._operation = operation

    @property
    def operation(self):
        """
        The unsupported operation requested.

        :rtype: str
        """
        return self._operation


class SpinnmanEIEIOPacketParsingException(SpinnmanException):
    """
    Unable to complete the parsing of the EIEIO packet received.
    The routine used is invalid or the content of the packet is invalid.
    """

    def __init__(self, parsing_format, packet):
        """
        :param str parsing_format:
        :param bytes packet:
        """
        super().__init__(
            "The packet received is being parsed as an EIEIO "
            f"{parsing_format} packet, "
            "but the content of the packet is invalid")
        self._packet = packet

    @property
    def packet(self):
        """
        :rtype: bytes
        """
        return self._packet


class SpiNNManCoresNotInStateException(SpinnmanTimeoutException):
    """
    Cores failed to reach a given state within a timeout.
    """

    def __init__(self, timeout, expected_states, failed_core_states):
        """
        :param float timeout:
        :param set(CPUState) expected_states:
        :param CPUInfos failed_core_states:
        """
        n_cores = len(failed_core_states)
        if n_cores > 10:
            msg = (f"waiting for {n_cores} cores to reach "
                   f"one of {expected_states}")
        else:
            msg = (f"waiting for cores {failed_core_states} to reach "
                   f"one of {expected_states}")
        super().__init__(msg, timeout, msg)
        self._failed_core_states = failed_core_states

    def failed_core_states(self):
        """
        :rtype: CPUInfos
        """
        return self._failed_core_states


class SpallocException(SpinnmanException):
    """
    Raised when there is a problem with the Spalloc session or job.
    """
