import logging
from threading import Thread
from multiprocessing.pool import ThreadPool

logger = logging.getLogger(__name__)
_POOL_SIZE = 4
_TIMEOUT = 1


class ConnectionListener(Thread):
    """ Thread that listens to a connection and calls callbacks with new\
        messages when they arrive.
    """
    __slots__ = [
        "_callback_pool",
        "_callbacks",
        "_connection",
        "_done",
        "_timeout"]

    def __init__(self, connection, n_processes=_POOL_SIZE, timeout=_TIMEOUT):
        """

        :param connection: An AbstractListenable connection to listen to
        :param n_processes: \
            The number of threads to use when calling callbacks
        """
        super(ConnectionListener, self).__init__(
            name="Connection listener for connection {}".format(connection))
        self.daemon = True
        self._connection = connection
        self._timeout = timeout
        self._callback_pool = ThreadPool(processes=n_processes)
        self._done = False
        self._callbacks = set()

    def _run_step(self, handler):
        if self._connection.is_ready_to_receive(timeout=self._timeout):
            message = handler()
            for callback in self._callbacks:
                self._callback_pool.apply_async(callback, [message])

    def run(self):
        handler = self._connection.get_receive_method()
        while not self._done:
            try:
                self._run_step(handler)
            except Exception:
                if not self._done:
                    logger.warn("problem when dispatching message",
                                exc_info=True)
        self._callback_pool.close()
        self._callback_pool.join()

    def add_callback(self, callback):
        """ Add a callback to be called when a message is received

        :param callback: A callable which takes a single parameter, which is\
                the message received
        :type callback: callable (connection message type -> None)
        """
        self._callbacks.add(callback)

    def close(self):
        """ Closes the listener.  Note that this does not close the provider\
            of the messages; this instead marks the listener as closed.  The\
            listener will not truly stop until the get message call returns.
        """
        self._done = True
        self.join()
