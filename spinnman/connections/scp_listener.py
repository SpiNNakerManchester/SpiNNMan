import threading

class SCPListener(threading.Thread):
    """ Listens for SCP packets received from a connection,\
        calling a callback function with received packets
    """

    def __init__(self, sdp_receiver, callback, error_callback=None):
        """
        :param connection: The SDP Receiver to receive packets from
        :type connection: spinnman.connections.abstract_sdp_receiver.AbstractSDPReceiver
        :param callback: The callback function to call on reception of each\
                    packet; the function should take one parameter, which is\
                    the SCP packet received
        :type callback: function(spinnman.messages.scp_message.SCPMessage)
        :param error_callback: The callback function to call if there is an\
                    error receiving a packet; the function should take two\
                    parameters:
                    * The exception received
                    * A message indicating what the problem was
        :type error_callback: function(Exception, str)
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If\
                    the callback or the error_callback do not take the\
                    expected number of arguments
        """
        pass

    def start(self):
        """ Starts listening and sending callbacks
        
        :return: Nothing is returned
        :rtype: None
        :raise None: No known exceptions are raised
        """
        pass
    
    def stop(self):
        """ Stops the reception of packets
        
        :return: Nothing is returned
        :rtype: None
        :raise None: No known exceptions are raised
        """
        pass
