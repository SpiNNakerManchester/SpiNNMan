from threading import Thread
import traceback
from multiprocessing.pool import ThreadPool


class ConnectionListener(Thread):
    """ Listens to a connection and calls callbacks with new messages when \
        they arrive
    """

    def __init__(self, connection, n_processes=4):
        """

        :param connection: An AbstractListenable connection to listen to
        :param n_processes: The number of threads to use when calling\
                callbacks
        """
        Thread.__init__(
            self,
            name="Connection listener for connection {}".format(connection))
        self._connection = connection
        self._get_message_call = connection.get_receive_method()
        self._callback_pool = ThreadPool(processes=n_processes)
        self._done = False
        self._callbacks = set()
        self.setDaemon(True)

    def run(self):
        while not self._done:
            try:
                if self._connection.is_ready_to_receive(timeout=1):
                    message = self._get_message_call()
                    for callback in self._callbacks:
                        self._callback_pool.apply_async(callback, [message])
            except:
                if not self._done:
                    traceback.print_exc()
        self._callback_pool.close()
        self._callback_pool.join()

    def add_callback(self, callback):
        """ Add a callback to be called when a message is received

        :param callback: A callable which takes a single parameter, which is\
                the message received
        """
        self._callbacks.add(callback)

    def close(self):
        """ Closes the listener.  Note that this does not close the provider\
            of the messages; this instead marks the listener as closed.  The\
            listener will not truly stop until the get message call returns.
        """
        self._done = True
        self.join()
