# Copyright (c) 2015 The University of Manchester
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from __future__ import annotations
import logging
from threading import Thread
from queue import Queue
from typing import Callable, Generic, List, TypeVar, Tuple, Optional
from spinn_utilities.log import FormatAdapter
from spinnman.exceptions import SpinnmanEOFException
from spinnman.connections.abstract_classes import Listenable

#: :meta private:
T = TypeVar("T")
logger = FormatAdapter(logging.getLogger(__name__))
_POOL_SIZE = 4
_MAX_QUEUE_SIZE = 100
_TIMEOUT = 1


class ConnectionListener(Thread, Generic[T]):
    """
    Thread that listens to a connection and calls callbacks with new
    messages when they arrive.
    """
    __slots__ = (
        "__process_threads",
        "__process_queue",
        "__callbacks",
        "__connection",
        "__done",
        "__timeout",
        "__drop_count")

    def __init__(self, connection: Listenable[T],
                 n_processes: int = _POOL_SIZE, timeout: float = _TIMEOUT,
                 max_queue_size: int = _MAX_QUEUE_SIZE) -> None:
        """
        :param connection: A connection to listen to
        :param n_processes:
            The number of threads to use when calling callbacks
        :param timeout:
            How long to wait for messages before checking to see if the
            connection is to be terminated.
        :param max_queue_size:
            The maximum size of the queue of messages to be processed.
        """
        super().__init__(
            name=f"Connection listener for connection {connection}")
        self.daemon = True
        self.__connection = connection
        self.__timeout = timeout
        self.__done = False
        self.__callbacks: List[Callable[[T], None]] = []
        self.__process_queue: Queue[Tuple[Callable, Optional[T]]] = Queue(
            maxsize=max_queue_size)
        self.__process_threads: List[_ProcessThread[T]] = [
            _ProcessThread(self.__process_queue)
            for _ in range(n_processes)
        ]
        self.__drop_count: int = 0

    def __run_step(self, handler: Callable[[], T]) -> None:
        """
        :param handler:
        """
        if self.__connection.is_ready_to_receive(timeout=self.__timeout):
            message = handler()
            for callback in self.__callbacks:
                if self.__process_queue.full():
                    self.__drop_count += 1
                else:
                    self.__process_queue.put((callback, message))

    def run(self) -> None:
        """
        Implements the listening thread.
        """
        self.__drop_count = 0
        for process_thread in self.__process_threads:
            process_thread.start()
        handler = self.__connection.get_receive_method()
        while not self.__done:
            try:
                self.__run_step(handler)
            except SpinnmanEOFException:
                self.__done = True
            except Exception:  # pylint: disable=broad-except
                if not self.__done:
                    logger.warning("problem when dispatching message",
                                   exc_info=True)
        for process_thread in self.__process_threads:
            process_thread.stop()
            process_thread.join()
        if self.__drop_count > 0:
            logger.warning(
                "{} messages were dropped due to full processing queue",
                self.__drop_count)

    def add_callback(self, callback: Callable[[T], None]) -> None:
        """
        Add a callback to be called when a message is received.

        :param callback:
            A callable which takes a single parameter, which is the message
            received; the result of the callback will be ignored.
        """
        self.__callbacks.append(callback)

    def close(self) -> None:
        """
        Closes the listener.

        .. note::
            This does not close the provider of the messages; this instead
            marks the listener as closed.  The listener will not truly stop
            until the get message call returns.
        """
        self.__done = True
        self.join()


class _ProcessThread(Thread, Generic[T]):
    """
    A thread that processes messages from a queue.
    """
    __slots__ = ("__process_queue", )

    def __init__(
            self, process_queue: Queue[Tuple[Callable, Optional[T]]]) -> None:
        """
        :param process_queue:
            The queue to get things to do from
        """
        super().__init__(daemon=True)
        self.__process_queue = process_queue

    def run(self) -> None:
        """
        The thread's main loop.
        """
        while True:
            callback, message = self.__process_queue.get()
            if message is None:
                break
            callback(message)

    def stop(self) -> None:
        """
        Stop the thread.
        """
        self.__process_queue.put((lambda x: None, None))
