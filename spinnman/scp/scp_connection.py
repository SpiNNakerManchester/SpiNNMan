__author__ = 'stokesa6'
#
# DESCRIPTION
#   A simple implementation of the SpiNNaker command protocol.
#
# AUTHORS
#   Kier J. Dugan - (kjd1v07@ecs.soton.ac.uk)
#
# DETAILS
#   Created on       : 11 May 2012
#   Revision         : $Revision: 271 $
#   Last modified on : $Date: 2013-02-26 17:10:16 +0000 (Tue, 26 Feb 2013) $
#   Last modified by : $Author: kjd1v07 $
#   $Id: scp.py 271 2013-02-26 17:10:16Z kjd1v07 $
#
# COPYRIGHT
#   Copyright (c) 2012 The University of Southampton.  All Rights Reserved.
#   Electronics and Electrical Engingeering Group,
#   School of Electronics and Computer Science (ECS)
#
from spinnman.sdp.sdp_connection import _SDPConnection
from spinnman.scp.scp_message import _SCPMessage
from spinnaker_tools_tools import scamp_constants
from spinnman import exceptions
from spinnaker_tools_tools.version_info import VersionInfo
import socket
import logging

logger = logging.getLogger(__name__)


class _SCPConnection(_SDPConnection):
    """
    Builds on an :py:class:`SDPConnection` to support the SpiNNaker Command\
    Protocol (SCP) which can interact with SC&MP and SARK.\
    \
    Example usage::\
    \
        conn = SCPConnection ('fiercebeast2', 17893)\
        conn.select ('root')\
        conn.set_iptag (0, 'localhost', 34521)\
        conn.select (1)\
        conn.write_mem_from_file (0x78000000, TYPE_WORD, 'myapp.aplx')\
        conn.exec_aplx (0x78000000)\
    \
    It is possible to send user-specific :py:class:`SCPMessage`\ s if the \
    target application uses the SCP packet format by simplying using the\
    :py:meth:`send` and :py:meth:`receive` methods with :py:class:`SCPMessage`\
    objects instead of :py:class:`SDPMessage`.  This class overrides both\
    methods to ensure that this works correctly, which means that the *context\
    manager* and *iterator* behaviours of :py:class:`SDPConnection` are\
    automatically supported by :py:class:`SCPConnection`.\
    \
    .. note::\
    \
        :py:class:`SCPConnection` maintains an internal record of a *selected*\
        processor and hence any :py:class:`SCPMessage`\ s sent will have their\
        target members changed to reflect this internal record.\
    \
    .. seealso::\
    \
        - :py:class:`SCPMessage`\
        - :py:class:`SDPConnection`\
        - :py:class:`SDPMessage`\
    """

    def __init__(self, host, port=17893):
        """Constructs a new :py:class:`SCPConnection` object.

        :param host: hostname of the remote SpiNNaker machine
        :param port: port number to communicate through
        :type host: str
        :type port: int
        :return a new SCP connection object
        :rtype:spinnman.scp.scp_connection.SCPConnection
        :raise:  None: does not raise any known exceptions
        """
        super(_SCPConnection, self).__init__(host, port)

        # intialise SCP members
        self._x = 0
        self._y = 0
        self._cpu = 0
        self._node = (self._x << 8) | self._y

        # initialise the sequence number counter
        self._seq = 0

        self.no_len_retries = 0
        self.no_timeout_retries = 0
        self.no_p2ptimeout_retries = 0

    def get_socketnames(self):
        """ helper method to get access to the sockets name
        :return the list of socket names
        :rtype: list
        :raise: None: does not raise any known exceptions
        """
        self._sock.getsockname()

    def reset_retries(self):
        """ resets a collection of counter used on this scp connection

        :return None
        :rtype:None
        :raise: None: does not raise any known exceptions
        """
        self.no_len_retries = 0
        self.no_timeout_retries = 0
        self.no_p2ptimeout_retries = 0

    def get_retries(self):
        """ return a collection of counters on retries and the types of retries

        :return number of timeout retries, number of p2ptime out retires and
                the number of no_len_retries
        :rtype: a tuple with names of {'time_out_retires',
               'p2p_time_out_retries', 'no_len_retries'}
        :raise: None: does not raise any known exceptions
        """
        return {'time_out_retires': self.no_timeout_retries,
                'p2p_time_out_retries': self.no_p2ptimeout_retries,
                'no_len_retries': self.no_len_retries}

    def set_view(self, new_x, new_y, new_cpu, new_node):
        """a helper method for positioning which chip and core to look at in \
           sark

        :param new_x: the new x chip location on the machine
        :param new_y: the new y chip location on the machine
        :param new_cpu: the new core/processor location on the machine
        :param new_node: the  X|Y co-ordinate id.
        :return:None
        :rtype: None
        :raise: None: does not raise any known exceptions
        """
        self._x = new_x
        self._y = new_y
        self._cpu = new_cpu
        self._node = new_node

    def __repr__(self):
        """Custom representation for interactive programming -- overridden from\
           SDPConnection.

        :return: a string represnetation of the SCP_connection
        :rtype: str
        :raise: None: does not raise any known exceptions
        """
        return 'SCPConnection: {:s}[{:s}]:{:d}'.format(self.remote_hostname,
                                                       self.remote_host_ip,
                                                       self.remote_host_port)

    @property
    def selected_node_coords(self):
        """(X, Y) co-ordinates of the selected node in P2P space.

        :return: a tuple containing x and y coords of the selected node
        :rtype: tuple
        :raise: None: does not raise any known exceptions
        """
        return {'x': self._x, 'y': self._y}

    @selected_node_coords.setter
    def selected_node_coords(self, new_coords):
        """set the (X, Y) co-ordinates of the selected node in P2P space.

        :param new_coords: a tuple containing the new coordinates of the
                           selected node
        :type new_coords: tuple
        :return: None
        :rtype: None
        :raise: None: does not raise any known exceptions
        """
        self._x = new_coords['x']
        self._y = new_coords['y']
        self._node = ((self._x & 0xFF) << 8) | (self._y & 0xFF)

    @property
    def selected_node(self):
        """Node P2P ID comprised of X|Y co-ordinates.

        :return: the  X|Y co-ordinate id.
        :rtype: int
        :raise: None: does not raise any known exceptions
        """
        return self._node

    @selected_node.setter
    def selected_node(self, new_id):
        """ changes the selected node

        :param new_id: the new  X|Y co-ordinate id of the selected node
        :type new_id: int
        :return: None
        :rtype: None
        :raise: None: does not raise any known exceptions
        """
        self._node = new_id
        (self._x, self._y) = ((new_id >> 8) & 0xFF, new_id & 0xFF)

    @property
    def selected_cpu(self):
        """Index of the selected CPU on the selected node.

        :return: the cpu currently selected
        :rtype: int
        :raise: None: does not raise any known exceptions
        """
        return self._cpu

    @selected_cpu.setter
    def selected_cpu(self, new_cpu):
        """ changes the selected cpu

        :param new_cpu: the new id for the new selected cpu
        :type new_cpu: int
        :return: None
        :rtype: None
        :raise: None: does not raise any known exceptions
        """
        self._cpu = new_cpu

    @property
    def selected_cpu_coords(self):
        """(X, Y, N) co-ordinates of the selected CPU (N) and node (X, Y).

        :return: a tuple containing (X, Y, N) co-ordinates of the selected
                 CPU (N) and node (X, Y).
        :rtype: typle
        :raise: None: does not raise any known exceptions
        """

        return {'x': self._x, 'y': self._y, 'p': self._cpu}

    @selected_cpu_coords.setter
    def selected_cpu_coords(self, new_coords):
        """set the (X, Y, N) co-ordinates of the selected CPU (N) and node \
           (X, Y).

        :param new_coords: the new (X, Y, N) co-ordinates of the selected \
               CPU (N) and node (X, Y).
        :type new_coords: tuple
        :return: None
        :rtype: None
        :raise: None: does not raise any known exceptions
        """
        (self._x, self._y, self._cpu) = new_coords
        self._node = ((self._x & 0xFF) << 8) | (self._y & 0xFF)

    def receive(self, msg_type=_SCPMessage):
        """Override from :py:class:`SDPConnection` to convert the socket data\
           into an :py:class:`SCPMessage` object (or whichever is required).

        :param msg_type: :py:class:`SCPMessage`-derived class to unpack response
        :type msg_type: a derived class of SCP_Message
        :return: a msg_type object
        :rtype: msg_type
        :raise: socket.error, socket.timeout, struct.error
        """
        return super(_SCPConnection, self).receive(msg_type)

    def send_scp_msg(self, msg, retries=10):
        """ Dispatches the given packet and expects a response from the target\
            machine.  Before the packet is sent, the destination co-ordinates\
            and CPU index are altered to match the values internal to this \
            class.

        :param msg: command packet to send to remote host
        :param retries: the number of times to try to transmit the message
                        before failing
        :type msg: _SCPMessage
        :type retries: int
        :return: :py:class:`SCPMessage` returned from the remote host
        :raise: spinnman.exceptions.SCPError
        """

        # update the message before sending
        msg.dst_cpu = self._cpu
        msg.dst_x = self._x
        msg.dst_y = self._y

        # get the response from the remote host
        sent_message = False
        resp = None
        self.next_seq_num()
        while not sent_message and retries > 0:
            try:
                self.send(msg)
                resp = self.receive()
                if ((resp.cmd_rc != scamp_constants.RC_TIMEOUT)
                        and (resp.cmd_rc != scamp_constants.RC_P2P_TIMEOUT)
                        and (resp.cmd_rc != scamp_constants.RC_LEN)):
                    sent_message = True
                else:
                    logger.debug("Warning - response was {}, retrying"
                                 .format(scamp_constants.
                                         rc_to_string(resp.cmd_rc)))
                    if resp.cmd_rc == scamp_constants.RC_TIMEOUT:
                        self.no_timeout_retries += 1
                    elif resp.cmd_rc == scamp_constants.RC_P2P_TIMEOUT:
                        self.no_p2ptimeout_retries += 1
                    elif resp.cmd_rc == scamp_constants.RC_LEN:
                        self.no_len_retries += 1
                    retries -= 1
            except socket.timeout:
                logger.debug("Warning - timeout waiting for response")
                retries -= 1
        if not sent_message:
            raise exceptions.SCPError(0, "Failed to receive response "
                                         "after sending message")

        # deal with errors by making it someone else's problem!
        if resp.cmd_rc != scamp_constants.RC_OK:
            raise exceptions.SCPError(resp.cmd_rc, resp)
        else:
            return resp

    def version(self, retries=10):
        """Retreives the version information about the host operating system.

        :param retries: the number of times to try to transmit the message\
                        before failing
        :type retries: int
        :return: version of OS in a class
        :rtype: spinnman.spinnaker_tools_tools.version_info.VersionInfo object
        :raise: spinnman.exceptions.SCPError
        """
        cmd_msg = _SCPMessage(cmd_rc=scamp_constants.CMD_VER)
        ver_msg = self.send_scp_msg(cmd_msg, retries=retries)
        # decode the payload into a usable struct
        return VersionInfo(ver_msg)

    def next_seq_num(self):
        """Generate a new sequence number for some of the SC&MP/SARK commands.

        :return: next sequence number
        :rtype: int
        :raise: None: does not raise any known exceptions
        """
        # mod 128 counter increment
        self._seq = (self._seq + 1) % 128
        return 2 * self._seq

    def init_p2p_tables(self, cx, cy):
        """Configure the P2P tables on the remote SpiNNaker using the \
           Manchester algorithm which superimposes a 2D co-ordinate space on \
           the SpiNNaker fabric.

        :param cx: width of the P2P space
        :param cy: height of the P2P space
        :type cx: int
        :type cy: int
        :return: None
        :rtype: None
        :raise: spinnman.exceptions.SCPError
        """

        msg = _SCPMessage(cmd_rc=scamp_constants.CMD_P2PC)

        # generate a new sequence number
        seq = self.next_seq_num()

        # the following lines have been taken almost verbatim from ybug.
        # the comments state the following organisation but this is clearly no
        # longer the case:
        #   arg1 = 00 : 00 :   00   : seq num
        #   arg2 = cx : cy : addr x : addr y
        #   arg3 = 00 : 00 :   fwd  :  retry
        msg.arg1 = (0x003e << 16) | seq
        msg.arg2 = (cx << 24) | (cy << 16)
        msg.arg3 = 0x3ff8

        # send the command to SpiNNaker
        self.send_scp_msg(msg)

    def set_leds(self, led1=scamp_constants.LED_NO_CHANGE,
                 led2=scamp_constants.LED_NO_CHANGE,
                 led3=scamp_constants.LED_NO_CHANGE,
                 led4=scamp_constants.LED_NO_CHANGE):
        """Changes the state of the LEDs of the target SpiNNaker node.\
        Each ``ledN`` parameter may be given one of four values from the SC&MP\
        definitions: ``LED_NO_CHANGE``, ``LED_INVERT``, ``LED_OFF``, or\
        ``LED_ON``.

        :param int led1: action for LED 1
        :param int led2: action for LED 2
        :param int led3: action for LED 3
        :param int led4: action for LED 4
        :return: None
        :rtype: None
        :raise: SCPError
        """

        # LED control signals exist only in the lowest byte of arg1
        msg = _SCPMessage()
        msg.cmd_rc = scamp_constants.CMD_LED
        msg.arg1 = (led4 << 6) | (led3 << 4) | (led2 << 2) | led1
        self.send_scp_msg(msg)
