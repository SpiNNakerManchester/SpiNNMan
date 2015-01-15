from threading import Condition


class _MessageCallback(object):
    """ A callback that is used to receive callbacks when a message is\
        sent, and again when a response is received.  The caller can\
        wait for a send to complete, and/or wait for a receipt of a message.
        If an exception has been thrown, this will be re-thrown by the wait\
        methods.
    """

    def __init__(self):
        self._message_sent_condition = Condition()
        self._message_sent = False
        self._message_send_exception = None
        self._message_send_traceback = None
        self._message_received_condition = Condition()
        self._message_received = None
        self._message_receive_exception = None
        self._message_receive_traceback = None

    def message_sent(self):
        """ Called when a message has been sent

        :return: Nothing is returned
        :rtype: None
        :raise None: No known exceptions are raised
        """
        self._message_sent_condition.acquire()
        self._message_sent = True
        self._message_sent_condition.notify_all()
        self._message_sent_condition.release()

    def send_exception(self, exception, traceback):
        """ Called when an exception has been received while sending a\
            message

        :param exception: An exception
        :type exception: :py:class:`spinnman.exceptions.SpinnmanException`
        :param traceback: A traceback of the exception
        :type traceback: traceback
        :return: Nothing is returned
        :rtype: None
        :raise None: No known exceptions are raised
        """
        self._message_sent_condition.acquire()
        self._message_send_exception = exception
        self._message_send_traceback = traceback
        self._message_sent_condition.notify_all()
        self._message_sent_condition.release()

    def wait_for_send(self):
        """ Waits for a send to be completed, or a send exception to be\
            received.  If an exception is received, this exception will be\
            raised, otherwise the function will return after the send is\
            complete.

        :return: Nothing is returned
        :rtype: None
        :raise spinnman.exceptions.SpinnmanException: If an exception is\
                    raised before the message has been sent
        """
        self._message_sent_condition.acquire()
        while not self._message_sent and self._message_send_exception is None:
            self._message_sent_condition.wait()
        self._message_sent_condition.release()

        if self._message_send_exception is not None:
            raise (self._message_send_exception, None,
                   self._message_send_traceback)

    def message_received(self, message):
        """ Called when a message has been received

        :return: Nothing is returned
        :rtype: None
        :raise None: No known exceptions are raised
        """
        self._message_received_condition.acquire()
        self._message_received = message
        self._message_received_condition.notify_all()
        self._message_received_condition.release()

    def receive_exception(self, exception, traceback):
        """ Called when an exception has been received while attempting to\
            receive a message

        :param exception: An exception
        :type exception: :py:class:`spinnman.exceptions.SpinnmanException`
        :param traceback: A traceback of the exception
        :type traceback: traceback
        :return: Nothing is returned
        :rtype: None
        :raise None: No known exceptions are raised
        """
        self._message_received_condition.acquire()
        self._message_receive_exception = exception
        self._message_receive_traceback = traceback
        self._message_received_condition.notify_all()
        self._message_received_condition.release()

    def wait_for_receive(self):
        """ Waits for a received message, or a receive exception to be\
            received.  If an exception is received, this exception will be\
            raised, otherwise the function will return the received message\
            after it has been received.

        :return: The message received
        :rtype: One of:
                    * :py:class:`spinnman.messages.sdp.sdp_message.SDPMessage`
                    * :py:class:`spinnman.messages.scp.abstract_scp_response.AbstractSCPResponse`
                    * :py:class:`spinnman.messages.multicast_message.MulticastMessage`
                    * :py:class:`spinnman.messages.spinnaker_boot.spinnaker_boot_message.SpinnakerBootMessage`
        :raise spinnman.exceptions.SpinnmanException: If an exception is raised\
                    before the message has been received
        """
        self._message_received_condition.acquire()
        while (self._message_received is None
                and self._message_receive_exception is None):
            self._message_received_condition.wait()
        self._message_received_condition.release()

        if self._message_receive_exception is not None:
            raise (self._message_receive_exception, "",
                   self._message_receive_traceback)

        return self._message_received
