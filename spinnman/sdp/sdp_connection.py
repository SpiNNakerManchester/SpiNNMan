__author__ = 'stokesa6'
import socket
import select
from spinnman.sdp.sdp_message import SDPMessage


class SDPConnection(object):
    """Represents an SDP connection to a target SpiNNaker machine or an
    incoming SDP connection to the local machine.\
    \
    Typical usage::\
    \
        conn = SDPConnection ('fiercebeast2')\
        msg  = SDPMessage ()\
        msg.dst_cpu  = 1\
        msg.dst_port = 7\
        msg.data     = "Hello!"\
        conn.send (msg)\
        conn.wait_for_message ()\
        response = conn.receive ()\
    \
    It is also to use this connection to set up an SDP server that can respond\
    to incoming SDP connections over the network::\
    \
        with SDPConnection ('localhost') as conn:\
            messages = 0\
            conn.listen (0.2) # wait for message for 0.2s or return None\
            for msg in conn:\
                if msg:\
                    print msg.data\
                    messages += 1\
                elif messages >= 100: # stop after 100 messages\
                    conn.interrupt ()\
    \
    The above example demonstrates two key features implemented by\
    :py:class:`SDPConnection`.  It can be iterated over using a ``for``-loop\
    which will return either a valid message or ``None`` if\
    :py:data:`iterator_timeout` has elapsed.  This allows the application to\
    perform behaviours even if a packet has not yet arrived, which is stopping\
    the iteration with :py:meth:`interrupt` in the case of the example above.\
    \
    :py:class:`SDPConnection` also implements a *context manager* which allows\
    it to be used as part of a ``with`` clause.  Clean-up is automatic if this\
    method is used and is hence useful when implementing servers.\
    \
    .. note::\
    \
        Clean-up is *still* automatic when using a ``with`` statement, even if\
        an exception is raised in the code because Python ensures that context\
        managers are informed of *all* changes of context regardless of the\
        cause.\
    \
    .. seealso::\
    \
        - :py:class:`SDPMessage`\
        - :py:class:`SCPMessage`\
        - :py:class:`SCPConnection`
    """

    def __init__(self, host='fiercebeast0', port=17893):
        """Constructs a :py:class:`SDPConnection` object.

        :param host: hostname of the target (or host if listening)
        :param port: port to send to (or one which to listen)
        :type host: str
        :type port: int
        :return: a new spinnman.sdp.sdp_connection.SDPConnection object
        :rtype: spinnman.sdp.sdp_connection.SDPConnection
        :raise: spinnman.spinnman_exceptions.InvalidHostNameException
        """
        self._sock = None

        # resolve the hostname to make things easier
        try:
            # resolving 'locahost' will find the correct hostname but will
            # *always* return an IP of 127.0.0.1 which seems to prevent external
            # connections under some conditions.
            if host.lower() in ('localhost', '127.0.0.1'):
                host = socket.gethostname()

            hostname, _, addresses = socket.gethostbyname_ex(host)
        except:
            raise ValueError('cannot resolve hostname %s' % host)
        # store the hostname and the host IP for messages
        self._hostname = hostname
        self._host = addresses[0]
        self._port = port
        self._addr = (self._host, port)
        self._interrupt = True
        self._iter_to = None

        # create a socket and enforce a small timeout
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.connect((addresses[0], port))
        self._sock.settimeout(1.0)  # 1 second
        self.remote_hostname = property(self._hostname,
                                        doc="Hostname of the remote SpiNNaker")
        self.remote_host_ip = property(self._host,
                                       doc="IPv4 address of the remote"
                                           " SpiNNaker")
        self.remote_host_port = property(self._port,
                                         doc="Port to connect to on the remote "
                                             "SpiNNaker")

    def __del__(self):
        """Class destructor -- closes any open network connections.

        :return: None
        :rtype: None
        :raise: None: does not raise any known exceptions
        """
        self.close()

    def __enter__(self):
        """Context manager -- enter new context.\
        There is no special behaviour required here because the network socket\
        is established in the class constructor.

        :return: None
        :rtype: None
        :raise: None: does not raise any known exceptions
        """
        return self

    def __exit__(self, exception_type):
        """Context manager -- leave existing context.\
        Special behaviour *may* be required here depending on the exception\
        raised.  A :py:exc:`StopIteration` may be suppressed as this is the\
        desired use case, but all other exceptions are probably genuine errors\
        that the user should care about.

        :param exception_type:      type of the exception
        :param value:     instance value of the exception
        :param traceback: stack trace up until the error
        :return: True or False
        :rtype: boolean
        :raise: None: does not raise any known exceptions
        """
        # close down the socket
        self.close()

        # context managers may return True to suppress an exception or anything
        # that will evaluate to False to allow it to propagate.  They must
        # *never* raise exceptions unless they themselves have failed.
        return exception_type is StopIteration

    def __repr__(self):
        """Custom representation for interactive programming.

        :return: a represnetation of the sdp connection
        :rtype: str
        :raise: None: does not raise any known exceptions
        """
        return 'SDPConnection: {:s}[{:s}]:{:d}'.format(self.remote_hostname,
                                                       self.remote_host_ip,
                                                       self.remote_host_port)

    def send(self, message):
        """Sends an :py:class:`SDPMessage` to the remote host.

        :param message: message packet to send
        :type message: spinnman.sdp.sdp_message.SDPMessage
        :return None
        :rtype: None
        :raise: socket.error, socket.timeout, struct.error
        """
        raw_data = str(message)
        self._sock.send(raw_data)

    def receive(self, msg_type=SDPMessage):
        """Recives data from the remote host and processes it into the required\
           object type (default is :py:class:`SDPMessage`).

        :param msg_type: :py:class:`SDPMessage`-derived class to unpack response
        :type msg_type: a object pointer, default set to a SDPMessage
        :return: a message of a given message type
        :rtype: the input msg_type
        :raise: socket.error, socket.timeout, struct.error
        """
        raw_data, addr = self._sock.recvfrom(512)
        return msg_type(raw_data)

    def has_message(self, timeout=0):
        """return ``True`` if there is a message in the buffer that should be\
           handled.

        :param timeout: maximum time (in seconds) to wait before returning
        :type timeout:  float or None
        :return a socket with a message
        :rtype: socket
        :raise: None: does not raise any known exceptions
        """

        rlist, wlist, xlist = select.select([self._sock], [], [], timeout)
        return self._sock in rlist

    def __nonzero__(self):
        """a helper method that return ``True`` if there is a message in the\
        buffer.

        :return: true or false
        :rtype: boolean
        :raise: None: does not raise any known exceptions
        """
        return self.has_message()

    def wait_for_message(self):
        """Spins indefinitely waiting for an :py:class:`SDPMessage` to arrive.

        :return: None
        :rtype: None
        :raise: None: does not raise any known exceptions
        """
        while True:
            if self.has_message(0.2):
                return

    def listen(self, timeout=None):
        """Binds the current socket to the hostname and port number given in
        the constructor so that messages may be delivered to this object.  This\
        process can be stopped by calling either :py:meth:`interrupt` or\
        :py:meth:`stop`.\
        \
        Usage::\
        \
            with SDPConnection ('localhost') as conn:\
                conn.listen ()\
                for msg in conn:\
                    print msg.data\
        \
        An optional timeout may be specified which is the maximum number of\
        seconds the iterator will wait for a packet.  If no packet arrives in\
        this interval then the iterator will return ``None`` which allows the\
        loop to do useful work between packet arrivals.  If ``timeout`` is\
        ``None`` (the default value) then each wait will block indefinitely.\
        \
        .. seealso:: \
        \
            :py:meth:`interrupt`\

        :param timeout: seconds to wait for a packet or ``None``
        :type timeout: float
        :return: None
        :rtype: None
        :raise: socket.error
        """
        # allow the iterator to run
        self._interrupt = False
        self._iter_to = timeout

        # bind the socket to the given port
        self._sock.bind((self._host, self._port))

    def close(self):
        """Closes the internal socket.

        :return: None
        :rtype: None
        :raise: socket.error
        """
        if self._sock:
            self._sock.close()
            self._sock = None

    def interrupt(self):
        """Stops the current iteration over the connection.

        :return: None
        :rtype: None
        :raise: None: does not raise any known exceptions
        """
        self._interrupt = True

    def _next(self):
        """Private function that actually performs the iterator behaviour for \
           :py:class:`_SDPConnectionIterator`.

        :return: a message of a given type recieved from a given socket
        :rtype: a msg_type or None
        :raise: None: does not raise any known exceptions
        """

        if self._interrupt is True:
            raise StopIteration

        if self.has_message(self._iter_to):
            return self.receive()
        else:
            return None

    def __iter__(self):
        """return an instance of an interator object for this class.

        :return a SDPConnectionIterator object
        :rtype: SDPConnectionIterator
        :raise: None: does not raise any known exceptions
        """
        return _SDPConnectionIterator(self)


# private classes (used by the __iter__ function in SDP_connection class)
#TODO ABS WHO USES THIS OBJECT AFTER THE SDP_CONNECTION???? is this a dead object
class _SDPConnectionIterator (object):
    """Iterator object that waits for messages on a :py:class:`SDPConnection`.
    """

    def __init__(self, conn):
        """Construct an _SDPConnectionIterator object for the given
           SDPConnection.

        :param conn: :py:class:`SDPConnection` to iterate over
        :type: spinnman.sdp.sdp_connection.SDPConnection object
        :return: None
        :rtype: None
        :raise: None: does not raise any known exceptions
        """

        self._conn = conn

    @property
    def next(self):
        """return the next packet in the SDP stream.

        :return: next :py:class:`SDPMessage` in the stream or ``None``
        :rtype: None or a spinnman.sdp.sdp_message.SDPMessage
        :raise: None: does not raise any known exceptions
        """
        return self._conn._next()
