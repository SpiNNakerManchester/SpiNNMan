from spinnman.messages.scp.scp_result import SCPResult
from spinnman.exceptions import SpinnmanTimeoutException
from spinnman.exceptions import SpinnmanUnexpectedResponseCodeException

from threading import Thread
from threading import Condition

from time import sleep


class _SCPMessageCallback(Thread):
    """ A threaded callback that is used with a _ConnectionQueue\
        for SCP, that can retry the send a number of times for a given set of\
        error conditions (and also retries on timeouts).
    """

    def __init__(self, message, connection_queue, retry_codes=(
                SCPResult.RC_P2P_TIMEOUT, SCPResult.RC_TIMEOUT,
                SCPResult.RC_LEN),
            n_retries=10, timeout=1):
        """
        :param message: The message to send
        :type message:\
                    :py:class:`spinnman.messages.scp.abstract_scp_request.AbstractSCPRequest`
        :param connection_queue: The connection queue to send the message with
        :type connection_queue:\
                    :py:class:`spinnman.connections._connection_queue._ConnectionQueue
        :param retry_codes: The response codes which will result in a\
                    retry if received as a response
        :type retry_codes: iterable of\
                    :py:class:`spinnman.messages.scp.scp_result.SCPResult`
        :param n_retries: The number of times to retry when a retry code is\
                received
        :type n_retries: int
        :param timeout: The timeout to use when receiving a response
        :type timeout: int
        :raise None: No known exceptions are raised
        """
        super(_SCPMessageCallback, self).__init__()
        self._message = message
        self._connection_queue = connection_queue
        self._retry_codes = retry_codes
        self._n_retries = n_retries
        self._timeout = timeout

        self._response_condition = Condition()
        self._response = None
        self._exception = None

    def run(self):
        """ Run method of the Thread.  Note that start should be called to\
            start the thread running.
        """
        retries_to_go = self._n_retries
        response = None
        timeout = None
        while retries_to_go >= 0:
            retry = False
            timeout = None
            try:
                response = self._connection_queue.send_message(
                        message=self._message, response_required=True,
                        timeout=self._timeout)

                if response.scp_response_header.result == SCPResult.RC_OK:
                    self._response_condition.acquire()
                    self._response = response
                    self._response_condition.notify_all()
                    self._response_condition.release()
                    return None

                if response.scp_response_header.result in self._retry_codes:
                    retry = True
            except SpinnmanTimeoutException as exception:
                retry = True
                timeout = exception
            except Exception as exception:
                self._response_condition.acquire()
                self._exception = exception
                self._response_condition.notify_all()
                self._response_condition.release()
                return None

            if retry:
                retries_to_go -= 1
                sleep(0.1)

        self._response_condition.acquire()
        if timeout is not None:
            self._exception = timeout
        else:
            self._exception = SpinnmanUnexpectedResponseCodeException(
                    "SCP", self._message.scp_request_header.command.name,
                    response.scp_response_header.result.name)
        self._response_condition.notify_all()
        self._response_condition.release()

    def get_response(self):
        """ Wait for and get the response

        :return: The received response
        :rtype: :py:class:`spinnman.messages.scp.abstract_scp_response.AbstractSCPResponse`
        :raise spinnman.exceptions.SpinnmanTimeoutException: If there is a\
                    timeout before a message is received
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If one\
                    of the fields of the received message is invalid
        :raise spinnman.exceptions.SpinnmanInvalidPacketException: If a packet\
                    is received that is not a valid response
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    sending the message or receiving the response
        :raise spinnman.exceptions.SpinnmanUnexpectedResponseCodeException: If\
                    the response is not one of the expected codes
        """
        self._response_condition.acquire()
        while self._response is None and self._exception is None:
            self._response_condition.wait()
        self._response_condition.release()

        if self._exception is not None:
            raise self._exception

        return self._response
