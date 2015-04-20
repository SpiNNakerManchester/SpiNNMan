import unittest
import spinnman.connections.listeners._callback_queue as c_q
test_queue = list()


def append_to_list(item):
    global test_queue
    test_queue.append(item)


class TestingCallbackQueue(unittest.TestCase):

    def setUp(self):
        global test_queue
        test_queue = list()

    def test_creating_empty_queue(self):
        global test_queue
        queue = c_q._CallbackQueue(append_to_list)
        self.assertEqual(queue._callback, append_to_list)
        self.assertFalse(queue._running)

    def test_add_items_to_queue(self):
        global test_queue
        queue = c_q._CallbackQueue(append_to_list)
        self.assertEqual(queue._callback, append_to_list)
        self.assertFalse(queue._running)
        for i in range(5):
            queue.add_item(i)

        for item in queue._queue:
            test_queue.append(item)
        self.assertTrue(queue._queue)
        self.assertEqual(test_queue, [4, 3, 2, 1, 0])

    def test_get_items_from_queue(self):
        global test_queue
        queue = c_q._CallbackQueue(append_to_list)
        self.assertEqual(queue._callback, append_to_list)
        self.assertFalse(queue._running)
        for i in range(5):
            queue.add_item(i)

        queue.start()
        while queue._queue:
            pass
        queue.stop()
        self.assertEqual(test_queue, [0, 1, 2, 3, 4])

    def test_stop_receiving_items_from_queue(self):
        global test_queue
        queue = c_q._CallbackQueue(append_to_list)
        self.assertEqual(queue._callback, append_to_list)
        self.assertFalse(queue._running)

        test_against_list = list()
        for i in range(1000):
            queue.add_item(i)
            test_against_list.append(i)

        queue.start()
        while len(test_queue) < 5:
            pass
        queue.stop()
        self.assertAlmostEqual(len(test_queue), len([0, 1, 2, 3, 4]), delta=2)
        self.assertNotEqual(test_queue, test_against_list)


if __name__ == '__main__':
    unittest.main()
