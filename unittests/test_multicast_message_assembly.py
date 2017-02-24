import unittest
import spinnman.messages.multicast_message as multicast_msg

__author__ = 'Petrut'


class TestMulticastMessage(unittest.TestCase):
    def test_create_new_multicast_message_without_payload(self):
        msg = multicast_msg.MulticastMessage(1)
        self.assertEqual(msg.key, 1)
        self.assertEqual(msg.payload, None)

    def test_create_new_multicast_message_with_payload(self):
        msg = multicast_msg.MulticastMessage(1, 100)
        self.assertEqual(msg.key, 1)
        self.assertEqual(msg.payload, 100)


if __name__ == '__main__':
    unittest.main()
