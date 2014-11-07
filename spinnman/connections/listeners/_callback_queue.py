from threading import Thread
from threading import Condition
from collections import deque


class _CallbackQueue(Thread):
    """ Consumes items from a _queue calling a callback function with each item
    """

    def __init__(self, callback):
        """
        :param callback: Callback function to call with each packet
        :type callback: callable
        """
        Thread.__init__(self)
        self._queue = deque()
        self._callback = callback
        self._running = False
        self._queue_condition = Condition()
        self.setDaemon(True)

    def add_item(self, item):
        """ Adds an item to the _queue

        :param item: The item to add
        :return: Nothing is returned
        :rtype: None
        """
        self._queue_condition.acquire()
        self._queue.appendleft(item)
        self._queue_condition.notify_all()
        self._queue_condition.release()

    def run(self):
        """ Overridden method of Thread - consumes the _queue.
        """
        self._running = True
        while self._running:
            self._queue_condition.acquire()
            while self._running and len(self._queue) == 0:
                self._queue_condition.wait()
            if self._queue:
                item = self._queue.pop()
                self._callback(item)
            self._queue_condition.release()

    def stop(self):
        """ Stops the _queue from transferring items
        """
        self._running = False
        self._queue_condition.acquire()
        self._queue_condition.notify_all()
        self._queue_condition.release()
