import socket

from spinnman.connections.abstract_classes.abstract_spinnaker_boot_sender \
    import AbstractSpinnakerBootSender
from spinnman.connections.abstract_classes.abstract_spinnaker_boot_receiver \
    import AbstractSpinnakerBootReceiver
from spinnman.connections.abstract_classes.abstract_udp_connection import \
    AbstractUDPConnection
from spinnman.exceptions import SpinnmanIOException
from spinnman.exceptions import SpinnmanTimeoutException
from spinnman.exceptions import SpinnmanInvalidParameterException
from spinnman.exceptions import SpinnmanInvalidPacketException
from spinnman.messages.spinnaker_boot.spinnaker_boot_message \
    import SpinnakerBootMessage
from spinnman.messages.spinnaker_boot.spinnaker_boot_message \
    import BOOT_MESSAGE_VERSION
from spinnman.messages.spinnaker_boot.spinnaker_boot_op_code \
    import SpinnakerBootOpCode
from spinnman.data.big_endian_byte_array_byte_reader \
    import BigEndianByteArrayByteReader
from spinnman.data.big_endian_byte_array_byte_writer \
    import BigEndianByteArrayByteWriter
from spinnman import constants
import select


class UDPBootConnection(AbstractUDPConnection,
                        AbstractSpinnakerBootSender,
                        AbstractSpinnakerBootReceiver):
    """ A connection to the spinnaker board that uses UDP to for booting
    """

    def __init__(self, local_host=None, local_port=None, remote_host=None,
                 remote_port=constants.UDP_BOOT_CONNECTION_DEFAULT_PORT):
        """
        :param local_host: The local host name or ip address to bind to.\
                    If not specified defaults to bind to all interfaces,\
                    unless remote_host is specified, in which case binding is\
                    _done to the ip address that will be used to send packets
        :type local_host: str
        :param local_port: The local port to bind to, between 1025 and 65535.\
                    If not specified, defaults to a random unused local port
        :type local_port: int
        :param remote_host: The remote host name or ip address to send packets\
                    to.  If not specified, the socket will be available for\
                    listening only, and will throw and exception if used for\
                    sending
        :type remote_host: str
        :param remote_port: The remote port to send packets to.  If\
                    remote_host is None, this is ignored.
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    setting up the communication channel
        """
        AbstractUDPConnection.__init__(
            self, local_host, local_port, remote_host, remote_port)

    def send_boot_message(self, boot_message):
        """ See :py:meth:`spinnman.connections.abstract_spinnaker_boot_sender.AbstractSpinnakerBootSender.send_boot_message`
        """
        if not self._can_send:
            raise SpinnmanIOException("Not connected to a remote host")

        # Create a writer for the mesage
        data_length = 0
        if boot_message.data is not None:
            data_length = len(boot_message.data)
        writer = BigEndianByteArrayByteWriter()

        # Put the headers into the message (big-endian)
        writer.write_short(BOOT_MESSAGE_VERSION)
        writer.write_int(boot_message.opcode.value)
        writer.write_int(boot_message.operand_1)
        writer.write_int(boot_message.operand_2)
        writer.write_int(boot_message.operand_3)

        # Put the data in to the packet
        if data_length > 0:
            writer.write_bytes(boot_message.data)

        # Send the packet
        try:
            self._socket.send(writer.data)
        except Exception as e:
            raise SpinnmanIOException(str(e))

    def receive_boot_message(self, timeout=None):
        """ See :py:meth:`spinnman.connections.abstract_spinnaker_boot_receiver.AbstractSpinnakerBootReceiver.receive_boot_message`
        """

        # Receive the data
        try:
            read_ready, _, _ = select.select([self._socket], [], [], timeout)
            if not read_ready:
                raise socket.timeout()
            raw_data = self._socket.recv(2048)
        except socket.timeout:
            raise SpinnmanTimeoutException("receive_scp_message", timeout)
        except Exception as e:
            raise SpinnmanIOException(str(e))

        # Create a reader
        packet = bytearray(raw_data)
        reader = BigEndianByteArrayByteReader(packet)

        opcode_value = None
        try:
            # Check the version
            version = reader.read_short()
            if version != 1:
                raise SpinnmanInvalidParameterException(
                    "boot message version", version,
                    "Only version 1 of the spinnaker boot protocol is"
                    " currently supported")

            # Read the values
            opcode_value = reader.read_int()
            opcode = SpinnakerBootOpCode(opcode_value)
            operand_1 = reader.read_int()
            operand_2 = reader.read_int()
            operand_3 = reader.read_int()
            data = reader.read_bytes()
            if len(data) == 0:
                data = None

            # Parse the header (big endian)
            message = SpinnakerBootMessage(
                opcode=opcode, operand_1=operand_1, operand_2=operand_2,
                operand_3=operand_3, data=data)
            return message
        except IOError as exception:
            raise SpinnmanIOException(str(exception))
        except EOFError:
            raise SpinnmanInvalidPacketException(
                "Boot", "Not enough bytes in the packet")
        except ValueError:
            raise SpinnmanInvalidParameterException(
                "opcode", opcode_value, "Unrecognized value")

    def connection_type(self):
        return constants.CONNECTION_TYPE.UDP_BOOT

    def supports_sends_message(self, message):
        if isinstance(message, SpinnakerBootMessage):
            return True
        else:
            return False