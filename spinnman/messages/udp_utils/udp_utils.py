from spinnman.exceptions import SpinnmanInvalidParameterException

_SDP_SOURCE_PORT = 7
_SDP_SOURCE_CPU = 31
_SDP_SOURCE_CHIP_X = 0
_SDP_SOURCE_CHIP_Y = 0


def update_sdp_header(sdp_header, default_sdp_tag):
        """ Apply defaults to the sdp header where the values have not been set

        :param sdp_header: The SDP header values
        :type sdp_header:\
                    :py:class:`spinnman.messages.sdp.sdp_header.SDPHeader`
        :return: Nothing is returned
        :rtype: None
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If the\
                    packet already has a source_port != 7, a source_cpu != 31,\
                    a source_chip_x != 0, or a source_chip_y != 0
        """
        if sdp_header.tag is None:
            sdp_header.tag = default_sdp_tag

        if sdp_header.source_port is not None:
            if sdp_header.source_port != _SDP_SOURCE_PORT:
                raise SpinnmanInvalidParameterException(
                    "message.source_port", str(sdp_header.source_port),
                    "The source port must be {} to work with this"
                    " connection".format(_SDP_SOURCE_PORT))
        else:
            sdp_header.source_port = _SDP_SOURCE_PORT

        if sdp_header.source_cpu is not None:
            if sdp_header.source_cpu != _SDP_SOURCE_CPU:
                raise SpinnmanInvalidParameterException(
                    "message.source_cpu", str(sdp_header.source_cpu),
                    "The source cpu must be {} to work with this"
                    " connection".format(_SDP_SOURCE_CPU))
        else:
            sdp_header.source_cpu = _SDP_SOURCE_CPU

        if sdp_header.source_chip_x is not None:
            if sdp_header.source_chip_x != _SDP_SOURCE_CHIP_X:
                raise SpinnmanInvalidParameterException(
                    "message.source_chip_x", str(sdp_header.source_chip_x),
                    "The source chip x must be {} to work with this"
                    " connection".format(_SDP_SOURCE_CHIP_X))
        else:
            sdp_header.source_chip_x = _SDP_SOURCE_CHIP_X

        if sdp_header.source_chip_y is not None:
            if sdp_header.source_chip_y != _SDP_SOURCE_CHIP_Y:
                raise SpinnmanInvalidParameterException(
                    "message.source_chip_y", str(sdp_header.source_chip_y),
                    "The source chip y must be {} to work with this"
                    " connection".format(_SDP_SOURCE_CHIP_Y))
        else:
            sdp_header.source_chip_y = _SDP_SOURCE_CHIP_Y
