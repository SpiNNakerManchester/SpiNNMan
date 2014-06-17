__author__ = 'stokesa6'
from spinnman.scp.scp_message import SCPMessage
from spinnman.scp.spinnaker_tools_tools import scamp_constants
from spinnman.interfaces.iptag import IPTag
import socket
import struct
import math


class IPTagCalls(object):

    def __init__(self, transceiver):
        """constructor for a IPTAG call object
        :param transceiver: the parent object which contains other calls
        :type transceiver: spinnman.interfaces.transceiver.Transciever
        :return: a new  IPTAG call object
        :rtype: spinnman.interfaces.transceiver_tools.iptag_calls.IPTAGCalls
        :raise: None: does not raise any known exceptions
        """
        self._x = 0
        self._y = 0
        self._cpu = 0
        self._node = (self._x << 8) | self._y
        self.transceiver = transceiver

    def get_iptag_table_info(self):
        """Retrieve the number of fixed and transient tags available as well as\
           the default timeout for all transient tags.

        :return: fixed record count, transient record count, default timeout in\
                 a tuple
        :rtype: tuple
        :raise: spinnman.spinnman_exceptions.SCPError
        """

        # build up the request according to the following formula:
        #   arg1 = 0 : command : 0 :    0
        #   arg2 = 0 :    0    : 0 : timeout
        #   arg3 = 0 :    0    : 0 :    0
        msg = SCPMessage()
        msg.cmd_rc = scamp_constants.CMD_IPTAG
        msg.arg1 = scamp_constants.IPTAG_TTO << 16
        msg.arg2 = 255                  # must be 16 or greater to be ignored
        msg.arg3 = 0
        resp_msg = self.transceiver.send_scp_msg(msg)

        # decode the response data (32bits) structured as follows:
        #   31:24 - max. number of fixed tags
        #   23:16 - max. number of transient tags
        #   15: 8 - reserved (0)
        #    7: 0 - transient timeout exponent
        if len(resp_msg.data) != 4:
            raise ValueError("insufficient data received in response.")
        (ttoe, trans, fixed) = struct.unpack('Bx2B', resp_msg.data)

        # convert the timeout into seconds using the equation:
        #    timeout = 10ms * 2^(ttoE - 1)
        timeout = (1 << (ttoe - 1)) * 0.01

        return {'fixed': fixed, 'trans': trans, 'timeout': timeout}

    def set_transient_iptag_timeout(self, timeout):
        """Sets the timeout for all transient IP-tags on the target machine.\
           .. note::\
        \
            On the SpiNNaker node, all timeouts are stored in an exponential\
            representation that limits the number of valid timeout durations to\
            a small set.  Timeouts are calculated (from the node's perspective)\
            as follows::\
        \
                timeout = 10ms * 2^(tto - 1)\
        \
            Hence timeout values passed into this function will be decomposed\
            into ``tto`` in the above equation.\
        :param timeout: timeout in *seconds*
        :return: None
        :rtype: None
        :type timeout: float
        :raise: SCPError

        """

        # convert the timeout into the exponent as explained above
        tto = int(math.ceil(math.log((timeout / 0.01), 2))) + 1
        if tto >= 16:
            raise ValueError("specific timeout is too large.")

        # set the new transient timeout
        #   arg1 = 0 : command : 0 :    0
        #   arg2 = 0 :    0    : 0 : timeout
        #   arg3 = 0 :    0    : 0 :    0
        msg = SCPMessage()
        msg.cmd_rc = scamp_constants.CMD_IPTAG
        msg.arg1 = scamp_constants.IPTAG_TTO << 16
        msg.arg2 = tto
        msg.arg3 = 0
        self.transceiver.send_scp_msg(msg)

    def get_iptag(self, index):
        """Retrieve an IP-tag from the target SpiNNaker machine.

        :param index: index in the IP-tag table.
        :type index: int
        :return: IP tag data in a :py:class:`IPTag`
        :rtype: spinnman.interfaces.iptag.IPTag object
        :raise: spinnman.spinnman_exceptions.SCPError
        """

        # build up the request as follows:
        #   arg1 = 0 : command : 0 :  tag
        #   arg2 = 0 :    0    : 0 : count
        #   arg3 = 0 :    0    : 0 :   0
        msg = SCPMessage()
        msg.cmd_rc = scamp_constants.CMD_IPTAG
        msg.arg1 = scamp_constants.IPTAG_GET << 16 | index
        msg.arg2 = 1
        msg.arg3 = 0
        resp_msg = self.transceiver.send_scp_msg(msg)

        # deconstruct the returned data
        if len(resp_msg.data) != 16:
            raise ValueError("insufficient data received in response.")
        (ip, mac, port, timeout, flags) = struct.unpack('<4s6s3H',
                                                        resp_msg.data)

        # format the IP and MAC addresses correctly
        ip = '.'.join(['%d' % ord(c) for c in ip])
        mac = ':'.join(['%02X' % ord(c) for c in mac])

        # return the data as a struct
        return IPTag(ip=ip, mac=mac, port=port, timeout=timeout/100.0,
                     flags=flags, index=index)

    def set_iptag(self, index, host, port):
        """
        Set an IP-tag record at the required index.

        :param index:   index in the IP-tag table
        :param host:    hostname or IP address of destination
        :param port:    port to use on destination
        :type index: int
        :type host: str
        :type port: int
        :return: record index in the IP-tag table
        :rtype: int
        :raise: spinnman.spinnman_exceptions.SCPError
        """

        # clamp the port and timeout to their appropriate ranges
        port &= 0xFFFF

        # ensure that the given hostname is always an IP
        if host.lower() in ("localhost", "127.0.0.1", "."):
            host = self.transceiver.conn.get_socketnames()[0]
        ip = socket.gethostbyname(host)

        # decompose the IP address into the component numbers and store in an
        # integer in REVERSE order so that it's correct after packing
        ip, segs = 0, ip.split('.')
        if len(segs) != 4:
            raise ValueError("IP address format is incorrect")
        for n, seg in enumerate(segs):
            ip |= (int(seg) << (8*n))

        msg = SCPMessage(cmd_rc=scamp_constants.CMD_IPTAG)
        msg.arg1 = scamp_constants.IPTAG_SET << 16 | (index & 0xFF)

        # the rest of the arguments follow the order:
        #   arg2 = port
        #   arg3 = IP
        msg.arg2 = port
        msg.arg3 = ip

        # fire off the packet
        self.transceiver.send_scp_msg(msg)

    def clear_iptag(self, index):
        """Removes an IP-tag from the remote SpiNNaker.

        :param index: index to remove from the table
        :type index: int
        :return: None
        :rtype: None
        :raise: spinnman.spinnman_exceptions.SCPError
        """

        # build up the request as follows:
        #   arg1 = 0 : command : 0 : tag
        #   arg2 = 0 :    0    : 0 :  0
        #   arg3 = 0 :    0    : 0 :  0
        msg = SCPMessage()
        msg.cmd_rc = scamp_constants.CMD_IPTAG
        msg.arg1 = (scamp_constants.IPTAG_CLR << 16) | index

        # fire off the command
        self.transceiver.send_scp_msg(msg)

    def get_all_iptags(self):
        """Retrieves all registered IP-tags from the target SpiNNaker machine.

        :return: list of :py:class:`Struct`\ s containing IP-tag information
        :rtype: list
        :raise: spinnman.spinnman_exceptions.SCPError
        """

        iptags = []

        # get the total number of possible IP tag records
        fixed, trans, timeout = self.get_iptag_table_info()

        # iterate over the possibilities
        for i in xrange(fixed + trans):
            iptag = self.get_iptag(i)

            # add valid records to the list
            if iptag.__dict__['flags'] & scamp_constants.IPTAG_VALID:
                iptags.append(iptag)

        # return whatever we found (possibly an empty list)
        return iptags