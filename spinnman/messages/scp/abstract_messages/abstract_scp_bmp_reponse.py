"""
AbstractSCPBMPResponse
"""

# spinnman imports
from .abstract_scp_response import AbstractSCPResponse


class AbstractSCPBMPResponse(AbstractSCPResponse):
    """
    represents a scp request thats tialored for the bmp connection
    """

    __slots__ = ()

    def __init__(self):
        AbstractSCPResponse.__init__(self)
