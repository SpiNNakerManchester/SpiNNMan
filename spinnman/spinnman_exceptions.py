__author__ = 'stokesa6'

from spinnman.scp.spinnaker_tools_tools import scamp

class SpinnmanException(Exception):
    """Superclass of all exceptions from the spinnman module.
    :raises None: does not raise any known exceptions"""
    pass

class InvalidResponseCodeException(SpinnmanException):
    """thrown when a response code from the spinnaker board
    is not recongised by spinnman
    :raises None: does not raise any known exceptions"""
    pass

class InvalidCommandCodeException(SpinnmanException):
    """thrown when a command code is not recongised by spinnman
    :raises None: does not raise any known exceptions
    """
    pass


class SCPError (RuntimeError):
    """Error response from target SpiNNaker.
    :param int rc: response code from target SpiNNaker.
    :param msg: :py:class:`SCPMessage` that caused the error or ``None``
    :raises None: does not raise any known exceptions
    """

    def __init__ (self, rc, msg=None):
        """Construct an :py:exc:`SCPError` object.
        :param rc: response code from target SpiNNaker.
        :param msg: the SCPMessage that caused the error
        :type rc: int
        :type msg: spinnman.scp.scp_message.SCPMessage or None
        :raises None: does not raise any known exceptions
        """
        # get a nice custom error message
        super (SCPError, self).__init__ (
            "command failed with error %s: '%s'" % scamp.rc_to_string (rc))

        # save the response code
        self.rc      = rc
        self.rc_text = scamp.rc_to_string(rc)
        self.message = msg__author__ = 'stokesa6'

