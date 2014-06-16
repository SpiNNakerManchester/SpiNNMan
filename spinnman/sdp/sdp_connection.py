__author__ = 'stokesa6'

class SDPConnection(object):
    """Represents an SDP connection to a target SpiNNaker machine or an incoming
       SDP connection to the local machine.

    Typical usage::

        conn = SDPConnection ('fiercebeast2')
        msg  = SDPMessage ()
        msg.dst_cpu  = 1
        msg.dst_port = 7
        msg.data     = "Hello!"
        conn.send (msg)
        conn.wait_for_message ()
        response = conn.receive ()

    It is also to use this connection to set up an SDP server that can respond
    to incoming SDP connections over the network::

        with SDPConnection ('localhost') as conn:
            messages = 0
            conn.listen (0.2) # wait for message for 0.2s or return None
            for msg in conn:
                if msg:
                    print msg.data
                    messages += 1
                elif messages >= 100: # stop after 100 messages
                    conn.interrupt ()

    The above example demonstrates two key features implemented by
    :py:class:`SDPConnection`.  It can be iterated over using a ``for``-loop
    which will return either a valid message or ``None`` if
    :py:data:`iterator_timeout` has elapsed.  This allows the application to
    perform behaviours even if a packet has not yet arrived, which is stopping
    the iteration with :py:meth:`interrupt` in the case of the example above.

    :py:class:`SDPConnection` also implements a *context manager* which allows
    it to be used as part of a ``with`` clause.  Clean-up is automatic if this
    method is used and is hence useful when implementing servers.

    .. note::

        Clean-up is *still* automatic when using a ``with`` statement, even if
        an exception is raised in the code because Python ensures that context
        managers are informed of *all* changes of context regardless of the
        cause.

    .. seealso::

        - :py:class:`SDPMessage`
        - :py:class:`SCPMessage`
        - :py:class:`SCPConnection`

    """

    def __init__ (self, host='fiercebeast0', port=17893):
        """Constructs a :py:class:`SDPConnection` object.

        :param host: hostname of the target (or host if listening)
        :param port: port to send to (or one which to listen)
        :type host: str
        :type port: int
        :return: a new spinnman.sdp.sdp_connection.SDPConnection object
        :rtype: spinnman.sdp.sdp_connection.SDPConnection
        :raises: spinnman.spinnman_exceptions.InvalidHostNameException
        """
        pass

    def __del__ (self):
        """Class destructor -- closes any open network connections.
        :return: None
        :rtype: None
        :raises: None: does not raise any known exceptions
        """
        self.close ()

    def __enter__ (self):
        """Context manager -- enter new context.
        There is no special behaviour required here because the network socket
        is established in the class constructor.
        :return: None
        :rtype: None
        :raises: None: does not raise any known exceptions
        """
        return self

    def __exit__ (self, type, value, traceback):
        """Context manager -- leave existing context.

        :param type:      type of the exception
        :param value:     instance value of the exception
        :param traceback: stack trace up until the error
        :return: True or False
        :rtype: boolean
        :raises: None: does not raise any known exceptions

        Special behaviour *may* be required here depending on the exception
        raised.  A :py:exc:`StopIteration` may be suppressed as this is the
        desired use case, but all other exceptions are probably genuine errors
        that the user should care about.
        """
        pass

