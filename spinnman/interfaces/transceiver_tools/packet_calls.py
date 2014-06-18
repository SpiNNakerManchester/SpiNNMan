__author__ = 'stokesa6'
from spinnman.scp.scp_message import _SCPMessage


class _PacketCalls(object):
    """packet specific commands are stored here for clarity"""

    def __init__(self, transceiver):
        """the packet calls object is used to contain calls which are specific\
           to reading / writing and accessing memory. These can be:\
           \
           reading memory (file or ram)\
           writing memory (file or ram)\
           slice a container into smaller chunks\

           :param transceiver: the parent object which contains other calls
           :type transceiver: spinnman.interfaces.transceiver.Transciever
           :return: a new packetCalls object
           :rtype: spinnman.interfaces.transceiver_tools.packet_calls._PacketCalls
           :raise: None: does not raise any known exceptions
        """

        self.transceiver = transceiver
        self.nn_id = 0

    def flood_fill(self, buf, region, mask, app_id, app_flags, base=0x67800000):
        """executes a flood fill of a buffer to all cores in a region that \
           respond to a given application id.

           :param buf: the data to flood fill down to a given set of chips/cores
           :param region: defines which chips/cores are to be flood filled
           :param mask: used to determine which cores are flood filled.
           :param app_id: which application this flood fill comes from
           :param app_flags: what behaviour is to occur after the flood fill
           :param base: the base location in SDRAM to start writing
           :type buf:
           :type region: int
           :type mask: int
           :type app_id: int
           :type app_flags: int
           :type base: hex value
           :return: None
           :rtype: None
           :raise spinnman.exceptions.SCPError: whens an error occurs at the \
                                                connection level
        """
        pass

    def nnp(self, key, data, sfr):
        """sends a nearest neighbour message

        :param key: entry for arg1 of a scp message
        :param data: the data inside a scp message
        :param sfr: entry for arg3 of a scp message
        :type key: int
        :type data: str
        :type sfr: int
        :return: None
        :rtype: None
        :raise spinnman.exceptions.SCPError: whens an error occurs at the \
                                             connection level
        """
        pass

    def next_id(self):
        """ returns the next id used for packet sending

        :return: new id
        :rtype: int
        :raise: None: does not raise any known exceptions
        """
        pass

    def send_scp_msg(self, command_code, arg1, arg2, arg3, payload):
        """ open method for end users to send any type of scp packet

        :param command_code: the command code used for this scp packet.
        :param arg1: data to be entered into arg1 of a scp message.
        :param arg2: data to be entered into arg2 of a scp message.
        :param arg3: data to be entered into arg3 of a scp message.
        :param payload: data to be entered into the payload of a scp message.
        :type arg1: int
        :type arg2: int
        :type arg3: int
        :type payload: int
        :return: None
        :rtype: None
        :raise spinnman.exceptions.SCPError: whens an error occurs at the \
                                             connection level
        """
        msg = _SCPMessage()
        msg.cmd_rc = command_code
        msg.arg1 = arg1
        msg.arg2 = arg2
        msg.arg3 = arg3
        msg.payload = payload

        self.transceiver.conn.send_scp_msg(msg)
