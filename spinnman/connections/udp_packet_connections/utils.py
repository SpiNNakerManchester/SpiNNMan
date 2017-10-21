_SDP_SOURCE_PORT = 7
_SDP_SOURCE_CPU = 31
_SDP_TAG = 0xFF


def update_sdp_header_for_udp_send(sdp_header, source_x, source_y):
    """ Apply defaults to the sdp header for sending over UDP

    :param sdp_header: The SDP header values
    :type sdp_header:\
                :py:class:`spinnman.messages.sdp.sdp_header.SDPHeader`
    :return: Nothing is returned
    """
    sdp_header.tag = _SDP_TAG
    sdp_header.source_port = _SDP_SOURCE_PORT
    sdp_header.source_cpu = _SDP_SOURCE_CPU
    sdp_header.source_chip_x = source_x
    sdp_header.source_chip_y = source_y
