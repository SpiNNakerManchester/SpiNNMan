__author__ = 'stokesa6'
import struct

# private classes
class VersionInfo (object):
    """
    SC&MP/SARK version information as returned by the SVER command.

    """

    def __init__ (self, msg):
        """
        Constructs a VersionInfo object.

        :param msg: :py:class:`SCPMessage` containing the information
        :type msg: Spinnman.scp.scp_message.SCP_Message object
        :return: a new version_info object
        :rtype: spinnMan.scp.spinnaker_tools_tools.version_info.VersionInfo
        :raises: None: does not raise any known exceptions
        """

        data = msg.data

        # version info is actually in the argN space but as byte data and the
        # string descriptor follows
        verinfo = struct.unpack ('< 4B 2H I', data[:12])
        desc    = data[12:].strip ('\x00')

        # update the members
        (self.v_cpu, self.p_cpu, self.node_y, self.node_x, self.size,
            self.ver_num, self.time) = verinfo
        self.desc = desc

        # decode the version number
        self.ver_num /= 100.0