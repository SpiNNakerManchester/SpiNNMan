# spinnman imports
from .scp_response import AbstractSCPResponse


class BMPResponse(AbstractSCPResponse):
    """ Represents an SCP request thats tailored for the BMP connection.
    """

    __slots__ = ()
