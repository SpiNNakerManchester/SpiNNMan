from six import add_metaclass

from spinn_utilities.abstract_base import AbstractBase, abstractmethod
from .connection import Connection


@add_metaclass(AbstractBase)
class SpinnakerBootReceiver(Connection):
    """ A receiver of Spinnaker boot messages
    """

    __slots__ = ()

    @abstractmethod
    def receive_boot_message(self, timeout=None):
        """ Receives a boot message from this connection.  Blocks\
            until a message has been received, or a timeout occurs.

        :param timeout: The time in seconds to wait for the message to arrive;\
                    if not specified, will wait forever, or until the\
                    connection is closed
        :type timeout: int
        :return: a boot message
        :rtype:\
                    :py:class:`spinnman.messages.spinnaker_boot.spinnaker_boot_message.SpinnakerBootMessage`
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    receiving the message
        :raise spinnman.exceptions.SpinnmanTimeoutException: If there is a\
                    timeout before a message is received
        :raise spinnman.exceptions.SpinnmanInvalidPacketException: If the\
                    received packet is not a valid spinnaker boot message
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If one\
                    of the fields of the spinnaker boot message is invalid
        """
        pass
