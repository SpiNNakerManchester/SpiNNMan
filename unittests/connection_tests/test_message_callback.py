import unittest
from spinnman.connections.listeners._message_callback import \
    _MessageCallback as MC
import thread
import time


def message_sent_after_n_seconds(self):
    time.sleep(1)
    self.message_sent()


def exception_raised_after_n_seconds(self, exception, traceback):
    time.sleep(1)
    self.send_exception(exception, traceback)


def message_received_after_n_seconds(self, message):
    time.sleep(1)
    self.message_received(message)


def exception_received_after_n_seconds(self, exception, traceback):
    time.sleep(1)
    self.receive_exception(exception, traceback)


class TestMessageCallback(unittest.TestCase):
    def test_setup_new_message_callback(self):
        mc = MC()
        self.assertFalse(mc._message_sent)
        self.assertEqual(mc._message_send_exception , None)
        self.assertEqual(mc._message_send_traceback , None)
        self.assertEqual(mc._message_receive_exception , None)
        self.assertEqual(mc._message_received , None)
        self.assertEqual(mc._message_receive_traceback , None)

    def test_sent_message_callback(self):
        mc = MC()
        mc.message_sent()
        self.assertTrue(mc._message_sent)
        self.assertEqual(mc._message_send_exception , None)
        self.assertEqual(mc._message_send_traceback , None)
        self.assertEqual(mc._message_receive_exception , None)
        self.assertEqual(mc._message_received , None)
        self.assertEqual(mc._message_receive_traceback , None)

    def test_received_message_callback(self):
        mc = MC()
        message = self
        mc.message_received(message)
        self.assertFalse(mc._message_sent)
        self.assertEqual(mc._message_send_exception , None)
        self.assertEqual(mc._message_send_traceback , None)
        self.assertEqual(mc._message_receive_exception , None)
        self.assertEqual(mc._message_received , message)
        self.assertEqual(mc._message_receive_traceback , None)

    def test_send_exception(self):
        mc = MC()
        exc = AssertionError
        trace = "Trace"
        mc.send_exception(exc, trace)

    def test_wait_for_send(self):
        mc = MC()
        thread.start_new_thread(message_sent_after_n_seconds,(mc,))
        mc.wait_for_send()

    def test_wait_for_send_exception(self):
        mc = MC()
        with self.assertRaises(EOFError):
            thread.start_new_thread(exception_raised_after_n_seconds,
                                    (mc, EOFError, None))
            mc.wait_for_send()

    def test_wait_for_receive(self):
        mc = MC()
        thread.start_new_thread(message_received_after_n_seconds,
                                (mc, "Hello. This is Test speaking."))
        self.assertEqual(mc.wait_for_receive(), "Hello. This is Test speaking.")

    def test_wait_for_receive_exception(self):
        mc = MC()
        with self.assertRaises(MemoryError):
            thread.start_new_thread(exception_received_after_n_seconds,
                                    (mc, MemoryError, None))
            mc.wait_for_receive()


if __name__ == '__main__':
    unittest.main()
