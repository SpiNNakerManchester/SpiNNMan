from abc import ABCMeta
from abc import abstractmethod
from six import add_metaclass

from spinnman.connections.abstract_connection import AbstractConnection


@add_metaclass(ABCMeta)
class AbstractSCPSender(AbstractConnection):
    """ A sender of SCP messages
    """
    
    @abstractmethod
    def send_scp_request(self, scp_request):
        """ Sends an SCP request down this connection
        
        :param scp_request: message packet to send
        :type scp_request:
                    :py:class:`spinnman.messages.scp.abstract_scp_request.AbstractSCPRequest`
        :return: Nothing is returned
        :rtype: None
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    sending the message
        """
        pass
