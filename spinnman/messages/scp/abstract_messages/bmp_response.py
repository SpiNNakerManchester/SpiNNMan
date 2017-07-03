"""
BMPResponse
"""

# spinnman imports
from .scp_response import AbstractSCPResponse


class BMPResponse(AbstractSCPResponse):
    """
    represents a scp request thats tialored for the bmp connection
    """

    __slots__ = ()

    def __init__(self):
        AbstractSCPResponse.__init__(self)
