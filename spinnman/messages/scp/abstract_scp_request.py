from abc import ABCMeta
from abc import abstractmethod
from six import add_metaclass


@add_metaclass(ABCMeta)
class AbstractSCPRequest(object):
    """ Represents an Abstract SCP Request
    """

    def __init__(self, sdp_header, scp_request_header, argument_1=None,
            argument_2=None, argument_3=None, data=None):
        """

        :param sdp_header: The SDP header of the request
        :type sdp_header:\
                    :py:class:`spinnman.messages.sdp.sdp_header.SDPHeader`
        :param scp_request_header: The SCP header of the request
        :type scp_request_header:\
                    :py:class:`spinnman.messages.scp.scp_request_header.SCPRequestHeader`
        :param argument_1: The first argument, or None if no first argument
        :type argument_1: int
        :param argument_2: The second argument, or None if no second argument
        :type argument_2: int
        :param argument_3: The third argument, or None if no third argument
        :type argument_3: int
        :param data: The optional data, or None if no data
        :type data: bytearray
        :raise None: No known exceptions are raised
        """
        self._sdp_header = sdp_header
        self._scp_request_header = scp_request_header
        self._argument_1 = argument_1
        self._argument_2 = argument_2
        self._argument_3 = argument_3
        self._data = data

    @property
    def sdp_header(self):
        """ The SDP header of the message

        :rtype: :py:class:`spinnman.message.sdp.sdp_header.SDPHeader`
        """
        return self._sdp_header

    @property
    def scp_request_header(self):
        """ The SCP request header of the message

        :rtype: :py:class:`spinnman.messages.scp.scp_request_header.SCPRequestHeader`
        """
        return self._scp_request_header

    @property
    def argument_1(self):
        """ The first argument, or None if no first argument

        :rtype: int
        """
        return self._argument_1

    @property
    def argument_2(self):
        """ The second argument, or None if no second argument

        :rtype: int
        """
        return self._argument_2

    @property
    def argument_3(self):
        """ The third argument, or None if no third argument

        :rtype: int
        """
        return self._argument_3

    @property
    def data(self):
        """ The data, or None if no data

        :rtype: bytearray
        """
        return self._data

    def write_scp_request(self, byte_writer):
        """ Write the scp request to the given writer

        :param byte_writer: The writer to write to
        :type byte_writer:\
                    :py:class:`spinnman.data.abstract_byte_writer.AbstractByteWriter`
        :return: Nothing is returned
        :rtype: None
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    writing the request
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If any\
                    required values have not been set
        """
        self._sdp_header.write_sdp_header(byte_writer)
        self._scp_request_header.write_scp_request_header(byte_writer)

        # Current implementation writes the arguments, or 0 if not present
        # i.e. there are always three arguments.  This could be modified
        # later to only send the arguments that are provided, but currently
        # SCAMP assumes that there are 3 arguments as far as I can see
        arguments = [self._argument_1, self._argument_2, self._argument_3]
        for argument in arguments:
            if argument is not None:
                byte_writer.write_int(argument)
            else:
                byte_writer.write_int(0)

        # Write any data
        if self._data is not None and len(self._data) > 0:
            byte_writer.write_bytes(self._data)

    @abstractmethod
    def get_scp_response(self):
        """ Get an SCP response message to be used to process any response\
            received

        :return: An SCP response, or None if no response is required
        :rtype: :py:class:`spinnman.messages.scp_response.SCPResponse`
        :raise None: No known exceptions are raised
        """
        pass
