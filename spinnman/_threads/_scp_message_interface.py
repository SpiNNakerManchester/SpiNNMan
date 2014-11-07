from spinnman.messages.scp.scp_result import SCPResult
from spinnman.exceptions import SpinnmanTimeoutException
from spinnman.exceptions import SpinnmanUnexpectedResponseCodeException

from threading import Condition

from time import sleep
import sys


class SCPMessageInterface(object):
    """ A thread for SCP, that can retry the send a number of times for a\
        given set of error conditions (and also retries on timeouts).
    """

    def __init__(self, transceiver, message, retry_codes=(
                 SCPResult.RC_P2P_TIMEOUT, SCPResult.RC_TIMEOUT,
                 SCPResult.RC_LEN),
                 n_retries=10, timeout=1, connection=None):
        """
        :param transceiver: The transceiver that will send the message
        :type transceiver: :py:class:`spinnman.transceiver.Transceiver`
        :param message: The message to send
        :type message:\
                    :py:class:`spinnman.messages.scp.abstract_scp_request.AbstractSCPRequest`
        :param retry_codes: The response codes which will result in a\
                    retry if received as a response
        :type retry_codes: iterable of\
                    :py:class:`spinnman.messages.scp.scp_result.SCPResult`
        :param n_retries: The number of times to retry when a retry code is\
                received
        :type n_retries: int
        :param timeout: The timeout to use when receiving a response
        :type timeout: int
        :param connection: A connection which can send and receive SCP\
                    messages
        :type connection:\
                    :py:class:`spinnman.connections.abstract_connection.AbstractConnection`
        :raise None: No known exceptions are raised
        """
        self._transceiver = transceiver
        self._message = message
        self._retry_codes = retry_codes
        self._n_retries = n_retries
        self._timeout = timeout

        self._response_condition = Condition()
        self._response = None
        self._exception = None
        self._traceback = None
        self._connection = connection

    def run(self):
        """ Run method of the Thread.  Note that start should be called to\
            start the thread running.
        """
        retries_to_go = self._n_retries
        response = None
        last_exception = None
        while retries_to_go >= 0:
            retry = False
            last_exception = None
            try:
                response = self._transceiver._send_message(
                    message=self._message, response_required=True,
                    timeout=self._timeout, connection=self._connection)

                if response.scp_response_header.result == SCPResult.RC_OK:
                    self._response_condition.acquire()
                    self._response = response
                    self._response_condition.notify_all()
                    self._response_condition.release()
                    return None

                if response.scp_response_header.result in self._retry_codes:
                    retry = True
            except SpinnmanUnexpectedResponseCodeException as exception:
                response_code = SCPResult[exception.response]
                if response_code in self._retry_codes:
                    print "Retry due to", response_code
                    retry = True
                    last_exception = exception
                else:
                    self._response_condition.acquire()
                    self._exception = exception
                    self._traceback = sys.exc_info()[2]
                    self._response_condition.notify_all()
                    self._response_condition.release()
                    return None
            except SpinnmanTimeoutException as exception:
                retry = True
                last_exception = exception
            except Exception as exception:
                self._response_condition.acquire()
                self._exception = exception
                self._traceback = sys.exc_info()[2]
                self._response_condition.notify_all()
                self._response_condition.release()
                return None

            if retry:
                retries_to_go -= 1
                sleep(0.1)

        self._response_condition.acquire()
        if last_exception is not None:
            self._exception = last_exception
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
            raise self._exception, None, self._traceback

        return self._response
