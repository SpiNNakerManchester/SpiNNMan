import unittest

from spinnman.connections.listeners.scp_listener import SCPListener
from spinnman.connections.abstract_classes.abstract_scp_receiver import AbstractSCPReceiver
from spinnman.connections.udp_packet_connections.udp_scp_connection import UDPSCPConnection
from spinnman.exceptions import SpinnmanInvalidParameterException


def print_message(message):
    return message

def print_error(error, message):
    print type(error), message

def print_message_with_default_value(message, default = None):
    return message

def print_errors_with_default_value(error, message, default = None):
    raise error

def print_message_varargs(*message):
    print message[0]

def print_errors_varargs(*args):
    raise args[0](args[1])

udp_conn = UDPSCPConnection(remote_host="192.168.240.253")

class MySCPReceiver(AbstractSCPReceiver):
    def __int__(self):
        pass

    def is_connected(self):
        return True

    def close(self):
        pass

    def receive_scp_response(self, scp_response, timeout=None):
        #udp_conn.receive_scp_response(scp_response, timeout)
        #return "This is a message"
        raise NotImplementedError

class TestSCPListener(unittest.TestCase):
    def test_new_default_listener(self):
        SCPListener(udp_conn, udp_conn, print_message)

    def test_new_listener(self):
        SCPListener(udp_conn, MySCPReceiver, print_message, print_error)

    def test_new_listener_with_invalid_number_of_error_callback_parameters(self):
        with self.assertRaises(SpinnmanInvalidParameterException):
            SCPListener(udp_conn, MySCPReceiver, print_message, print_message)

    def test_new_listener_with_invalid_number_of_callback_parameters(self):
        with self.assertRaises(SpinnmanInvalidParameterException):
            SCPListener(udp_conn, MySCPReceiver, print_error, print_message)

    def test_new_default_listener_with_default_callback_parameters(self):
        SCPListener(udp_conn, MySCPReceiver, print_message_with_default_value)

    def test_new_listener_with_default_callback_parameters(self):
        SCPListener(udp_conn, MySCPReceiver,
                    print_message_with_default_value, print_errors_with_default_value)

    def test_new_listener_with_varargs_message_parameters(self):
        SCPListener(udp_conn, MySCPReceiver,
                    print_message_with_default_value, print_errors_varargs)

    def test_run_listener(self):
        listener = SCPListener(MySCPReceiver(),
                               MySCPReceiver, print_message, print_error)
        listener.start()
        # time.sleep(1)
        listener.stop()



if __name__ == '__main__':
    unittest.main()
