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
from SpiNNMan.spinnman.sdp.sdp_connection import SDPConnection

# class that wraps up the SCP protocol
class SCPConnection (SDPConnection):
    """
    Builds on an :py:class:`SDPConnection` to support the SpiNNaker Command
    Protocol (SCP) which can interact with SC&MP and SARK.

    Example usage::

        conn = SCPConnection ('fiercebeast2', 17893)
        conn.select ('root')
        conn.set_iptag (0, 'localhost', 34521)
        conn.select (1)
        conn.write_mem_from_file (0x78000000, TYPE_WORD, 'myapp.aplx')
        conn.exec_aplx (0x78000000)

    It is possible to send user-specific :py:class:`SCPMessage`\ s if the target
    application uses the SCP packet format by simplying using the
    :py:meth:`send` and :py:meth:`receive` methods with :py:class:`SCPMessage`
    objects instead of :py:class:`SDPMessage`.  This class overrides both
    methods to ensure that this works correctly, which means that the *context
    manager* and *iterator* behaviours of :py:class:`SDPConnection` are
    automatically supported by :py:class:`SCPConnection`.

    .. note::

        :py:class:`SCPConnection` maintains an internal record of a *selected*
        processor and hence any :py:class:`SCPMessage`\ s sent will have their
        target members changed to reflect this internal record.

    .. seealso::

        - :py:class:`SCPMessage`
        - :py:class:`SDPConnection`
        - :py:class:`SDPMessage`

    """

    def __init__ (self, host, port=17893):
        """Constructs a new :py:class:`SCPConnection` object.

        :param host: hostname of the remote SpiNNaker machine
        :param port: port number to communicate through
        :type host: str
        :type port: int
        :return a new SCP connection object
        :rtype:spinnman.scp.scp_connection.SCPConnection
        :raises:  None: does not raise any known exceptions
        """
        super (SCPConnection, self).__init__ (host, port)

        # intialise SCP members
        self._x     = 0
        self._y     = 0
        self._cpu   = 0
        self._node  = (self._x << 8) | self._y

        # initialise the sequence number counter
        self._seq = 0

        self.no_len_retries = 0
        self.no_timeout_retries = 0
        self.no_p2ptimeout_retries = 0

    def reset_retries(self):
        """ resets a collection of counter used on this scp connection
        :return None
        :rtype:None
        :raises: None: does not raise any known exceptions
        """
        self.no_len_retries = 0
        self.no_timeout_retries = 0
        self.no_p2ptimeout_retries = 0

    def get_retries(self):
        """ returns a collection of counters on retries and the types of retries
        :return number of timeout retries, number of p2ptime out retires and
                the number of no_len_retries
        :rtype: a tuple with names of {'time_out_retires',
               'p2p_time_out_retries', 'no_len_retries'}
        :raises: None: does not raise any known exceptions
        """
        return {'time_out_retires': self.no_timeout_retries,
                'p2p_time_out_retries': self.no_p2ptimeout_retries,
                'no_len_retries': self.no_len_retries}

    def set_view(self, new_x, new_y, new_cpu, new_node):
        """a helper method for positioning which chip and core to look at in
        sark
        :param new_x: the new x chip location on the machine
        :param new_y: the new y chip location on the machine
        :param new_cpu: the new core/processor location on the machine
        :param new_node: the  X|Y co-ordinate id.
        :return:
        """
        self._x = new_x
        self._y = new_y
        self._cpu = new_cpu
        self._node = new_node