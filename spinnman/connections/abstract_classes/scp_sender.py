from six import add_metaclass

from spinn_utilities.abstract_base \
    import AbstractBase, abstractmethod, abstractproperty
from .connection import Connection


@add_metaclass(AbstractBase)
class SCPSender(Connection):
    """ A sender of SCP messages
    """

    __slots__ = ()

    @abstractmethod
    def get_scp_data(self, scp_request):
        """ Returns the data of an SCP request as it would be sent down this\
            connection
        """

    @abstractmethod
    def send_scp_request(self, scp_request):
        """ Sends an SCP request down this connection

         Messages must have the following properties:

            * source_port is None or 7
            * source_cpu is None or 31
            * source_chip_x is None or 0
            * source_chip_y is None or 0

        tag in the message is optional - if not set the default set in the\
        constructor will be used.
        sequence in the message is optional - if not set (sequence number\
        last assigned + 1) % 65536 will be used

        :param scp_request: message packet to send
        :type scp_request:\
                    :py:class:`spinnman.messages.scp.abstract_scp_request.AbstractSCPRequest`
        :return: Nothing is returned
        :rtype: None
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    sending the message
        """

    @abstractproperty
    def chip_x(self):
        """ The x-coordinate of the chip at which messages sent down this\
            connection will arrive at first

        :rtype: int
        """

    @abstractproperty
    def chip_y(self):
        """ The y-coordinate of the chip at which messages sent down this\
            connection will arrive at first

        :rtype: int
        """
