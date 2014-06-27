from spinnman.connections.abstract_sdp_sender import AbstractSDPSender
from spinnman.connections.abstract_sdp_receiver import AbstractSDPReceiver
from spinnman.connections.abstract_scp_sender import AbstractSCPSender
from spinnman.connections.abstract_scp_receiver import AbstractSCPReceiver
from spinnman.connections.abstract_spinnaker_boot_sender import AbstractSpinnakerBootSender
from spinnman.connections.abstract_spinnaker_boot_receiver import AbstractSpinnakerBootReceiver

class UDPConnection(
        AbstractSDPSender, AbstractSDPReceiver, 
        AbstractSCPSender, AbstractSCPReceiver,
        AbstractSpinnakerBootSender, AbstractSpinnakerBootReceiver):
    """ A connection to the spinnaker board that uses UDP to send and/or\
        receive data
    """
    
    def __init__(self, local_host=None, local_port=None, remote_host=None,
            remote_port=17893):
        """
        :param local_host: The local host name or ip address to bind to.\
                    If not specified defaults to bind to all interfaces, unless\
                    remote_host is specified, in which case binding is done to\
                    the ip address that will be used to send packets
        :type local_host: str
        :param local_port: The local port to bind to, between 1025 and 65535.\
                    If not specified, defaults to a random unused local port
        :type local_port: int
        :param remote_host: The remote host name or ip address to send packets\
                    to.  If not specified, the socket will be available for\
                    listening only, and will throw and exception if used for\
                    sending
        :type remote_host: str
        :param remote_port: The remote port to send packets to.  If remote_host\
                    is None, this is ignored.
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    setting up the communication channel
        """
        pass
    
    @property
    def local_ip_address(self):
        """ The local IP address to which the connection is bound.
        
        :return: The local ip address as a dotted string e.g. 0.0.0.0
        :rtype: str
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    getting the local address
        """
        pass

    def send_sdp_message(self, sdp_message):
        """ See :py:meth:`spinnman.connections.abstract_sdp_sender.AbstractSDPSender.send_sdp_message`
        """
        # TODO
        pass
    
    def receive_sdp_message(self, timeout=None):
        """ See :py:meth:`spinnman.connections.abstract_sdp_receiver.AbstractSDPReceiver.receive_sdp_message`
        """
        # TODO
        return None
    
    def send_scp_message(self, sdp_message):
        """ See :py:meth:`spinnman.connections.abstract_scp_sender.AbstractSCPSender.send_scp_message`
        """
        # TODO
        pass
    
    def receive_scp_message(self, timeout=None):
        """ See :py:meth:`spinnman.connections.abstract_scp_receiver.AbstractSCPReceiver.receive_scp_message`
        """
        # TODO
        return None
    
    def send_boot_message(self, boot_message):
        """ See :py:meth:`spinnman.connections.abstract_spinnaker_boot_sender.AbstractSpinnakerBootSender.send_boot_message`
        """
        # TODO
        pass
    
    def receive_boot_message(self, timeout=None):
        """ See :py:meth:`spinnman.connections.abstract_spinnaker_boot_receiver.AbstractSpinnakerBootReceiver.receive_boot_message`
        """
        # TODO
        return None
