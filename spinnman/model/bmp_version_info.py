"""
BMPVersionInfo
"""


class BMPVersionInfo(object):
    """
    Decodes SC&MP/SARK version information as returned by the SVER command from
    a BMP connection
    """

    def __init__(self, version_data):
        """
        :param version_data: bytes from an SCP packet containing version\
                    information
        :type version_data: bytearray
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If the\
                    message does not contain valid version information
        """
