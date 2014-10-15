from threading import Thread
from threading import Condition
from collections import deque
import sys
import logging

from spinnman.connections._message_callback import _MessageCallback
from spinnman.messages.sdp.sdp_message import SDPMessage
from spinnman.connections.abstract_sdp_sender import AbstractSDPSender
from spinnman.exceptions import SpinnmanUnsupportedOperationException
from spinnman.exceptions import SpinnmanInvalidPacketException
from spinnman.connections.abstract_sdp_receiver import AbstractSDPReceiver
from spinnman.messages.scp.abstract_messages.abstract_scp_request import AbstractSCPRequest
from spinnman.connections.abstract_scp_sender import AbstractSCPSender
from spinnman.connections.abstract_scp_receiver import AbstractSCPReceiver
from spinnman.messages.multicast_message import MulticastMessage
from spinnman.connections.abstract_multicast_sender \
    import AbstractMulticastSender
from spinnman.connections.abstract_multicast_receiver \
    import AbstractMulticastReceiver
from spinnman.messages.spinnaker_boot.spinnaker_boot_message \
    import SpinnakerBootMessage
from spinnman.connections.abstract_spinnaker_boot_sender \
    import AbstractSpinnakerBootSender
from spinnman.connections.abstract_spinnaker_boot_receiver \
    import AbstractSpinnakerBootReceiver


logger = logging.getLogger(__name__)


class _ConnectionQueue(Thread):
    """ A queue of messages to be sent down a connection, and callbacks\
        to be called when a message has been sent and/or received.
    """

    def __init__(self, connection):
        """

        :param connection: The connection to use to send messages and\
                    receive responses
        :type connection: :py:class:`spinnman.connections.abstract_connection.AbstractConnection`
        :raise None: No known exceptions are raised
        """
        Thread.__init__(self)
        # Store the calls
        self._connection = connection

        # Set up a queue for the messages
        self._message_queue = deque()

        # Set up a queue for the callbacks
        self._callback_queue = deque()

        # Set up a queue which indicates whether a response is expected
        self._wait_for_response_queue = deque()

        # Set up a queue for the timeout
        self._timeout_queue = deque()

        # Set up a condition for thread control
        self._queue_condition = Condition()

        # Marker to indicate if the queue has been closed
        self._done = False

        self.setDaemon(True)

    def _check_message_type(self, message, response_required):
        """ Check if the message type is supported, raising an exception if not

        :param message: The message to determine support for
        :type message: One of:
                    * :py:class:`spinnman.messages.sdp.sdp_message.SDPMessage`
                    * :py:class:`spinnman.messages.scp.abstract_scp_request.SCPRequest`
                    * :py:class:`spinnman.messages.multicast_message.MulticastMessage`
                    * :py:class:`spinnman.messages.spinnaker_boot.spinnaker_boot_message.SpinnakerBootMessage`
        :param response_required: True if a response is required, False\
                    otherwise
        :type response_required: bool
        :return: Nothing is returned
        :rtype: None
        :raise spinnman.exceptions.SpinnmanUnsupportedOperationException: If\
                    the message type is unsupported
        :raise spinnman.exceptions.SpinnmanInvalidPacketException: If the\
                    message type is not recognized
        """
        if isinstance(message, SDPMessage):
            if not isinstance(self._connection, AbstractSDPSender):
                raise SpinnmanUnsupportedOperationException(
                    "Send SDP Message")
            if response_required and not isinstance(self._connection,
                                                    AbstractSDPReceiver):
                raise SpinnmanUnsupportedOperationException(
                    "Receive SDP Message")

        elif isinstance(message, AbstractSCPRequest):
            if not isinstance(self._connection, AbstractSCPSender):
                raise SpinnmanUnsupportedOperationException(
                    "Send SCP Message")
            if response_required and not isinstance(self._connection,
                                                    AbstractSCPReceiver):
                raise SpinnmanUnsupportedOperationException(
                    "Receive SCP Message")

        elif isinstance(message, MulticastMessage):
            if not isinstance(self._connection, AbstractMulticastSender):
                raise SpinnmanUnsupportedOperationException(
                    "Send Multicast Message")
            if response_required and not isinstance(self._connection,
                                                    AbstractMulticastReceiver):
                raise SpinnmanUnsupportedOperationException(
                    "Receive Multicast Message")
        elif isinstance(message, SpinnakerBootMessage):
            if not isinstance(self._connection, AbstractSpinnakerBootSender):
                raise SpinnmanUnsupportedOperationException(
                    "Send Spinnaker Boot Message")
            if response_required and not isinstance(
                    self._connection, AbstractSpinnakerBootReceiver):
                raise SpinnmanUnsupportedOperationException(
                    "Receive Spinnaker Boot Message")
        else:
            raise SpinnmanInvalidPacketException(
                message.__class__, "This type is not known to this class")

    def message_type_supported(self, message, response_required):
        """ Determine if a given message type is supported by this queue

        :param message: The message to determine support for
        :type message: One of:
                    * :py:class:`spinnman.messages.sdp.sdp_message.SDPMessage`
                    * :py:class:`spinnman.messages.scp.abstract_scp_request.AbstractSCPRequest`
                    * :py:class:`spinnman.messages.multicast_message.MulticastMessage`
                    * :py:class:`spinnman.messages.spinnaker_boot.spinnaker_boot_message.SpinnakerBootMessage`
        :param response_required: True if a response is required, False\
                    otherwise
        :type response_required: bool
        :return: True if the message type is supported, False otherwise
        :rtype: bool
        :raise spinnman.exceptions.SpinnmanInvalidPacketException: If the\
                    message type is not recognized
        """
        try:
            self._check_message_type(message, response_required)
            return True
        except SpinnmanUnsupportedOperationException:
            return False

    @property
    def queue_length(self):
        """ Get the current length of the queue

        :return: The length of the queue
        :rtype: int
        """
        return len(self._message_queue)

    def send_message(self, message, response_required, timeout):
        """ Send a message, waiting for the response if requested

        :param message: A message to be sent
        :type message: One of:
                    * :py:class:`spinnman.messages.sdp.sdp_message.SDPMessage`
                    * :py:class:`spinnman.messages.scp.abstract_scp_request.AbstractSCPRequest`
                    * :py:class:`spinnman.messages.multicast_message.MulticastMessage`
                    * :py:class:`spinnman.messages.spinnaker_boot.spinnaker_boot_message.SpinnakerBootMessage`
        :param response_required: True if a response is required, False\
                    otherwise
        :type response_required: bool
        :param timeout: The timeout for a response in seconds
        :type timeout: int
        :return: A message in response
        :rtype: Same type as the received message
        :raise spinnman.exceptions.SpinnmanTimeoutException: If there is a\
                    timeout before a message is received
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If one\
                    of the fields of the received message is invalid
        :raise spinnman.exceptions.SpinnmanInvalidPacketException:
                    * If the message is not one of the indicated types
                    * If a packet is received that is not a valid response
        :raise spinnman.exceptions.SpinnmanUnsupportedOperationException: If\
                    the connection cannot send the type of message given
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    sending the message or receiving the response
        """

        callback = self.send_message_non_blocking(message, response_required,
                                                  timeout)

        # Wait for the callback to indicate completion
        callback.wait_for_send()
        if response_required:
            return callback.wait_for_receive()
        return None

    def send_message_non_blocking(self, message, response_required, timeout):
        """ Send a message but return immediately

        :param message: A message to be sent
        :type message: One of:
                    * :py:class:`spinnman.messages.sdp.sdp_message.SDPMessage`
                    * :py:class:`spinnman.messages.scp.abstract_scp_request.AbstractSCPRequest`
                    * :py:class:`spinnman.messages.multicast_message.MulticastMessage`
                    * :py:class:`spinnman.messages.spinnaker_boot.spinnaker_boot_message.SpinnakerBootMessage`
        :param response_required: True if a response is required, False\
                    otherwise
        :type response_required: bool
        :param timeout: The timeout for a response in seconds
        :type timeout: int
        :return: A message callback object which can be used to wait for the\
                    message to be sent, or for a response
        :rtype: :py:class:`spinnman.connections._message_callback._MessageCallback`
        :raise spinnman.exceptions.SpinnmanTimeoutException: If there is a\
                    timeout before a message is received
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If one\
                    of the fields of the received message is invalid
        :raise spinnman.exceptions.SpinnmanInvalidPacketException:
                    * If the message is not one of the indicated types
                    * If a packet is received that is not a valid response
        :raise spinnman.exceptions.SpinnmanUnsupportedOperationException: If\
                    the connection cannot send the type of message given
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    sending the message or receiving the response
        """
        # Check that the connection can deal with the message
        self._check_message_type(message, response_required)

        # Create a callback for the message
        callback = _MessageCallback()

        # Add the details to the queues
        self._queue_condition.acquire()
        self._message_queue.appendleft(message)
        self._callback_queue.appendleft(callback)
        self._wait_for_response_queue.appendleft(response_required)
        self._timeout_queue.appendleft(timeout)
        self._queue_condition.notify_all()
        self._queue_condition.release()

        return callback

    def run(self):
        """ The main method of the thread
        """
        while not self._done:

            # Wait for a message to appear in the queue
            self._queue_condition.acquire()
            while not self._done and len(self._message_queue) == 0:
                self._queue_condition.wait()

            # If there is a message, get it
            message = None
            callback = None
            wait_for_response = None
            timeout = None
            if not self._done:
                message = self._message_queue.pop()
                callback = self._callback_queue.pop()
                wait_for_response = self._wait_for_response_queue.pop()
                timeout = self._timeout_queue.pop()

            # Release the queue
            self._queue_condition.release()

            if not self._done:

                # Send the message
                send_error = False
                logger.debug("Sending message {}".format(message))
                try:
                    if isinstance(message, SDPMessage):
                        logger.debug("Sending SDP message {}".format(message))
                        self._connection.send_sdp_message(message)
                    elif isinstance(message, AbstractSCPRequest):
                        logger.debug("Sending SCP message {}".format(message))
                        self._connection.send_scp_request(message)
                    elif isinstance(message, MulticastMessage):
                        logger.debug("Sending Multicast message {}".format(
                            message))
                        self._connection.send_multicast_message(message)
                    elif isinstance(message, SpinnakerBootMessage):
                        logger.debug("Sending Boot message {}".format(message))
                        self._connection.send_boot_message(message)
                    logger.debug("Message sent - notifying callback")
                    callback.message_sent()
                except Exception as exception:
                    callback.send_exception(exception, sys.exc_info()[2])
                    send_error = True

                # If there was no error, and a response is required,
                # get the response
                if not send_error and wait_for_response:
                    try:
                        response = None
                        if isinstance(message, SDPMessage):
                            logger.debug("Waiting for SDP response,"
                                         " timeout={}".format(timeout))
                            response = self._connection.receive_sdp_message(
                                timeout=timeout)
                        elif isinstance(message, AbstractSCPRequest):
                            logger.debug("Waiting for SCP response,"
                                         " timeout={}".format(timeout))
                            response = message.get_scp_response()
                            self._connection.receive_scp_response(
                                scp_response=response,
                                timeout=timeout)
                        elif isinstance(message, MulticastMessage):
                            logger.debug("Waiting for Multicast response,"
                                         " timeout={}".format(timeout))
                            response =\
                                self._connection.receive_multicast_message(
                                    timeout=timeout)
                        elif isinstance(message, SpinnakerBootMessage):
                            logger.debug("Waiting for Boot response,"
                                         " timeout={}".format(timeout))
                            response = self._connection.receive_boot_message(
                                timeout=timeout)
                        logger.debug("Response received - notifying callback")
                        callback.message_received(response)
                    except Exception as exception:
                        callback.receive_exception(exception,
                                                   sys.exc_info()[2])

    def stop(self):
        """ Stop the queue thread
        """
        self._queue_condition.acquire()
        self._done = True
        self._queue_condition.notify_all()
        self._queue_condition.release()
