from spinnman.messages.eieio.data_messages \
    import EIEIODataMessage, EIEIODataHeader


def read_eieio_data_message(data, offset):
    """ Reads the content of an EIEIO data message and returns an object\
        identifying the data which was contained in the packet

    :param data: data received from the network as a bytestring
    :type data: str
    :param offset: offset at which the parsing operation should start
    :type offset: int
    :return: an object which inherits from EIEIODataMessage which contains\
            parsed data received from the network
    :rtype:\
            :py:class:`spinnman.messages.eieio.data_messages.eieio_data_message.EIEIODataMessage`
    """
    eieio_header = EIEIODataHeader.from_bytestring(data, offset)
    offset += eieio_header.size
    return EIEIODataMessage(eieio_header, data, offset)
