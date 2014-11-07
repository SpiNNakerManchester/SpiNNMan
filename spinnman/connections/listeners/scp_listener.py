import inspect
from threading import Thread

from spinnman.connections.listeners._callback_queue import _CallbackQueue
from spinnman.exceptions import SpinnmanInvalidParameterException


def _function_has_free_argument_count(func, count):
    """ Determines if a function has a given free argument count (such that the
        function can be called with the given number of arguments)

    :param func: The function to determine the free argument count of
    :type func: callable
    :param count: The amount of free arguments to check for
    :type count: int
    :return: True if func has count free arguments, false otherwise
    :rtype: bool
    """
    (args, varargs, keywords, defaults) = inspect.getargspec(func)

    # If the function has count args, it is fine
    if len(args) == count:
        return True

    # If the function has count args once the defaults are assigned, it is fine
    if defaults and len(args) - len(defaults) == count:
        return True

    # Otherwise, if the function has a "varargs" or "keywords", it is fine
    if varargs is not None or keywords is not None:
        return True

    # Otherwise it must not match
    return False


class SCPListener(Thread):
    """ Listens for SCP packets received from a connection,\
        calling a callback function with received packets
    """

    def __init__(self, scp_receiver, response_class, callback,
                 error_callback=None):
        """
        :param scp_receiver: The SCP Receiver to receive packets from
        :type scp_receiver:\
                    :py:class:`spinnman.connections.abstract_scp_receiver.AbstractSCPReceiver`
        :param response_class: The SCP response
        :type response_class: class of implementation of\
                    :py:class:`spinnman.messages.scp.abstract_scp_response.AbstractSCPResponse`
        :param callback: The callback function to call on reception of each\
                    packet; the function should take one parameter, which is\
                    the SCP packet received
        :type callback: function(\
                    :py:class:`spinnman.messages.scp.abstract_scp_response.AbstractSCPResponse`)
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
        Thread.__init__(self)
        if not _function_has_free_argument_count(callback, 1):
            raise SpinnmanInvalidParameterException(
                "callback", repr(callback),
                "Incorrect number of parameters")

        if (error_callback is not None
                and not _function_has_free_argument_count(error_callback, 2)):
            raise SpinnmanInvalidParameterException(
                "error_callback", repr(error_callback),
                "Incorrect number of parameters")

        self._scp_receiver = scp_receiver
        self._response_class = response_class
        self._error_callback = error_callback
        self._queue_consumer = _CallbackQueue(callback)
        self._running = False

        self.setDaemon(True)

    def start(self):
        """ Starts listening and sending callbacks

        :return: Nothing is returned
        :rtype: None
        :raise None: No known exceptions are raised
        """
        self._queue_consumer.start()
        super(SCPListener, self).start()

    def run(self):
        """ Overridden method of Thread that runs this listener
        """
        self._running = True
        scp_response = self._response_class()
        while self._running and self._scp_receiver.is_connected():
            try:
                self._scp_receiver.receive_scp_response(scp_response)
                self._queue_consumer.add_item(scp_response)
            except Exception as exception:
                self._running = False
                self._error_callback(exception, "Error receiving packet")
        self.stop()

    def stop(self):
        """ Stops the reception of packets

        :return: Nothing is returned
        :rtype: None
        :raise None: No known exceptions are raised
        """
        self._running = False
        self._queue_consumer.stop()
