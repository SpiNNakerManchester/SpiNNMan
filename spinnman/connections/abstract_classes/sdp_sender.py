from six import add_metaclass

from spinn_utilities.abstract_base import AbstractBase, abstractmethod
from .connection import Connection


@add_metaclass(AbstractBase)
class SDPSender(Connection):
    """ A sender of SDP messages
    """

    __slots__ = ()

    @abstractmethod
    def send_sdp_message(self, sdp_message):
        """ Sends an SDP message down this connection

        :param sdp_message: The SDP message to be sent
        :type sdp_message: spinnman.messages.sdp.sdp_message.SDPMessage
        :return: Nothing is returned
        :rtype: None
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    sending the message
        """
