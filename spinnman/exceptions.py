__author__ = 'stokesa6'

from spinnman.scp.spinnaker_tools_tools.scamp_constants import rc_map, cc_map


class SpinnmanException(Exception):
    """Superclass of all exceptions from the spinnman module.

    :raise None: does not raise any known exceptions"""
    pass


class SpinnmanInvalidResponseCodeException(SpinnmanException):
    """thrown when a response code from the spinnaker board\
       is not recongised by spinnman

    :raise None: does not raise any known exceptions"""
    pass


class SpinnmanInvalidCommandCodeException(SpinnmanException):
    """thrown when a command code is not recongised by spinnman\

    :raise None: does not raise any known exceptions
    """
    pass


class SpinnmanStructInterpertationException(SpinnmanException):
    """thrown when a struct unpack cannot recongise aspects of the string \
    inside SpinnMan

    :raise None: does not raise any known exceptions
    """
    pass


class SpinnmanUnrecogonisedAttributeException(SpinnmanException):
    """thrown when a attribute is set that does not exist inside SpinnMan\

    :raise None: does not raise any known exceptions
    """
    pass


class SpinnmanUnrecogonisedHostNameException(SpinnmanException):
    """thrown when trying to make a sdp or scp connection with a invalid\
       hostname

    :raise None: does not raise any known exceptions
    """
    pass


class SpinnmanBootException(SpinnmanException):
    """thrown when trying to boot a spiNNaker machine fails

    :raise None: does not raise any known exceptions
    """
    pass


class SpinnmanInvalidIPTagConfigurationException(SpinnmanException):
    """thrown when a IPTAG is unable to be created due to incorrect parameters

    :raise None: does not raise any known exceptions
    """
    pass


class SpinnmanInvalidSignalException(SpinnmanException):
    """ thrown when a app signal is given which does not exist in the code base

    :raise None: does not raise any known exceptions
    """
    pass


class SpinnmanInvalidStateException(SpinnmanException):
    """ thrown when a app state is given which does not exist in the code base \
        or that a core has gone into a unexpected state

    :raise None: does not raise any known exceptions
    """
    pass


class SpinnmanExploreException(SpinnmanException):
    """ thrown when an attempt to explore the machine results in an error

    :raise None: does not raise any known exceptions
    """
    pass


class SpinnmanSCPError (RuntimeError):
    """Error response from target SpiNNaker.

    :param int rc: response code from target SpiNNaker.
    :param msg: :py:class:`SCPMessage` that caused the error or ``None``
    :raise None: does not raise any known exceptions
    """

    def __init__(self, rc, msg=None):
        """Construct an :py:exc:`SCPError` object.

        :param rc: response code from target SpiNNaker.
        :param msg: the SCPMessage that caused the error
        :type rc: int
        :type msg: spinnman.scp._scp_message.SCPMessage or None
        :raise None: does not raise any known exceptions
        """
        # get a nice custom error message
        super(SpinnmanSCPError, self).__init__("command failed with error "
                                               "{%s}: {%s}"
                                               .format(SpinnmanSCPError.
                                                       rc_to_string(rc), rc))
        # save the response code
        self.rc = rc
        self.rc_text = self.rc_to_string(rc)
        self.message = msg

    @staticmethod
    def rc_to_string(rc):
        """Returns the string equivalent of ``rc`` along with a very brief \
        description of what probably caused the error.

        :param rc: response code
        :type rc: int
        :returns: tuple of (string equivalent, description)
        :raises: KeyError
        """

        if rc not in rc_map.keys():
            raise SpinnmanInvalidResponseCodeException("do not recognise the "
                                                       "response code")
        return rc_map[rc]

    @staticmethod
    def cmd_to_string(cc):
        """Returns the string equivalent of the given command code.

        :param int cc: command code
        :returns: string name of ``cc``
        :raises: KeyError
        """

        if cc not in cc_map.keys():
            raise SpinnmanInvalidCommandCodeException("do not recognise the "
                                                      "command code")
        return cc_map[cc]