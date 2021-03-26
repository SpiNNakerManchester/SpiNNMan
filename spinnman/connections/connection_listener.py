# Copyright (c) 2017-2019 The University of Manchester
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging
from threading import Thread
from concurrent.futures import ThreadPoolExecutor
from spinn_utilities.abstract_context_manager import AbstractContextManager
from spinn_utilities.log import FormatAdapter

logger = FormatAdapter(logging.getLogger(__name__))
_POOL_SIZE = 4
_TIMEOUT = 1


class ConnectionListener(Thread, AbstractContextManager):
    """ Thread that listens to a connection and calls callbacks with new\
        messages when they arrive.
    """
    __slots__ = [
        "__callback_pool",
        "__callbacks",
        "__connection",
        "__done",
        "__timeout"]

    def __init__(self, connection, n_processes=_POOL_SIZE, timeout=_TIMEOUT):
        """
        :param Listenable connection: A connection to listen to
        :param int n_processes:
            The number of threads to use when calling callbacks
        :param float timeout:
            How long to wait for messages before checking to see if the
            connection is to be terminated.
        """
        super().__init__(
            name="Connection listener for connection {}".format(connection))
        self.daemon = True
        self.__connection = connection
        self.__timeout = timeout
        self.__callback_pool = ThreadPoolExecutor(max_workers=n_processes)
        self.__done = False
        self.__callbacks = set()

    def __run_step(self, handler):
        """
        :param callable handler:
        """
        if self.__connection.is_ready_to_receive(timeout=self.__timeout):
            message = handler()
            for callback in self.__callbacks:
                future = self.__callback_pool.submit(callback, message)
                future.add_done_callback(self.__done_callback)

    def __done_callback(self, future):
        """
        :param ~concurrent.futures.Future future:
        """
        try:
            future.result()
        except Exception:  # pylint: disable=broad-except
            logger.exception("problem in listener call")

    def run(self):
        """ Implements the listening thread.
        """
        try:
            handler = self.__connection.get_receive_method()
            while not self.__done:
                try:
                    self.__run_step(handler)
                except Exception:  # pylint: disable=broad-except
                    if not self.__done:
                        logger.warning("problem when dispatching message",
                                       exc_info=True)
        finally:
            self.__callback_pool.shutdown()
            self.__callback_pool = None

    def add_callback(self, callback):
        """ Add a callback to be called when a message is received

        :param callable callback:
            A callable which takes a single parameter, which is the message
            received; the result of the callback will be ignored.
        """
        self.__callbacks.add(callback)

    def close(self):
        """ Closes the listener.  Note that this does not close the provider\
            of the messages; this instead marks the listener as closed.  The\
            listener will not truly stop until the get message call returns.
        """
        self.__done = True
        self.join()
