from spinnman.exceptions import SpinnmanInvalidParameterException
from spinnman.exceptions import SpinnmanIOException
from spinnman.exceptions import SpinnmanInvalidPacketException
from spinnman.messages.sdp.sdp_flag import SDPFlag


class SDPHeader(object):
    """ Represents the header of an SDP message.
        Each optional parameter in the constructor can be set to a value other\
        than None once, after which it is immutable.  It is an error to set a\
        parameter that is not currently None.
    """

    def __init__(self, flags=None, tag=None,
                 destination_port=None, destination_cpu=None,
                 destination_chip_x=None, destination_chip_y=None,
                 source_port=None, source_cpu=None,
                 source_chip_x=None, source_chip_y=None):
        """
        :param flags: Any flags for the packet
        :type flags: :py:class:`spinnman.messages.sdp.sdp_flag.SDPFlag`
        :param tag: The ip tag of the packet between 0 and 255, or None if it\
                    is to be set later
        :type tag: int
        :param destination_port: The destination port of the packet between 0\
                    and 7
        :type destination_port: int
        :param destination_cpu: The destination processor id within the chip\
                    between 0 and 31
        :type destination_cpu: int
        :param destination_chip_x: The x-coordinate of the destination chip\
                    between 0 and 255
        :type destination_chip_x: int
        :param destination_chip_y: The y-coordinate of the destination chip\
                    between 0 and 255
        :type destination_chip_y: int
        :param source_port: The source port of the packet between 0 and 7, or\
                    None if it is to be set later
        :type source_port: int
        :param source_cpu: The source processor id within the chip\
                   between 0 and 31, or None if it is to be set later
        :type source_cpu: int
        :param source_chip_x: The x-coordinate of the source chip\
                    between 0 and 255, or None if it is to be set later
        :type source_chip_x: int
        :param source_chip_y: The y-coordinate of the source chip\
                    between 0 and 255, or None if it is to be set later
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If one\
                    ofthe parameters is not valid
        """
        self._flags = None
        self._tag = None
        self._destination_port = None
        self._destination_cpu = None
        self._destination_chip_x = None
        self._destination_chip_y = None
        self._source_port = None
        self._source_cpu = None
        self._source_chip_x = None
        self._source_chip_y = None

        self.flags = flags
        self.tag = tag
        self.destination_port = destination_port
        self.destination_cpu = destination_cpu
        self.destination_chip_x = destination_chip_x
        self.destination_chip_y = destination_chip_y
        self.source_port = source_port
        self.source_cpu = source_cpu
        self.source_chip_x = source_chip_x
        self.source_chip_y = source_chip_y

    @property
    def flags(self):
        """ The flags of the packet

        :return: The flags of the packet
        :rtype: :py:class:`spinnman.messages.sdp.sdp_flag.SDPFlag`
        """
        return self._flags

    @flags.setter
    def flags(self, flags):
        """ Set the flags of the packet

        :param flags: The flags to set
        :type flags: :py:class:`spinnman.messages.sdp.sdp_flag.SDPFlag`
        :return: Nothing is returned
        :rtype: None
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If the\
                    flags have already been set
        """
        if self._flags is not None:
            raise SpinnmanInvalidParameterException(
                "flags", flags.name, "Already set")
        self._flags = flags

    @property
    def tag(self):
        """ The tag of the packet

        :return: The tag of the packet between 0 and 255
        :rtype: int
        """
        return self._tag

    @tag.setter
    def tag(self, tag):
        """ Set the tag of the packet

        :param tag: The tag to set, between 0 and 255
        :type tag: int
        :return: Nothing is returned
        :rtype: None
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If the\
                    tag has already been set or if the value is out of range
        """
        if self._tag is not None:
            raise SpinnmanInvalidParameterException(
                "tag", str(tag), "Already set")
        if tag is not None and (tag < 0 or tag > 255):
            raise SpinnmanInvalidParameterException(
                "tag", str(tag), "Must be between 0 and 255")

        self._tag = tag

    @property
    def destination_port(self):
        """ The destination port of the packet

        :return: The destination port of the packet between 0 and 7
        :rtype: int
        """
        return self._destination_port

    @destination_port.setter
    def destination_port(self, destination_port):
        """ Set the destination port of the packet

        :param destination_port: The destination port to set, between 0 and 7
        :type destination_port: int
        :return: Nothing is returned
        :rtype: None
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If the\
                    destination_port has already been set or if the value is\
                    out of range
        """
        if self._destination_port is not None:
            raise SpinnmanInvalidParameterException(
                "destination_port", str(destination_port), "Already set")
        if destination_port is not None and (destination_port < 0
                                             or destination_port > 7):
            raise SpinnmanInvalidParameterException(
                "destination_port", str(destination_port),
                "Must be between 0 and 7")

        self._destination_port = destination_port

    @property
    def destination_cpu(self):
        """ The core on the destination chip

        :return: The core on the destination chip, between 0 and 31
        :rtype: int
        """
        return self._destination_cpu

    @destination_cpu.setter
    def destination_cpu(self, destination_cpu):
        """ Set the id of the destination processor of the packet

        :param destination_cpu: The processor id to set, between 0 and 31
        :type destination_cpu: int
        :return: Nothing is returned
        :rtype: None
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If the\
                    destination_cpu has already been set or if the value is\
                    out of range
        """
        if self._destination_cpu is not None:
            raise SpinnmanInvalidParameterException(
                "destination_cpu", str(destination_cpu), "Already set")
        if destination_cpu is not None and (destination_cpu < 0
                                            or destination_cpu > 31):
            raise SpinnmanInvalidParameterException(
                "destination_cpu", str(destination_cpu),
                "Must be between 0 and 31")

        self._destination_cpu = destination_cpu

    @property
    def destination_chip_x(self):
        """ The x-coordinate of the destination chip of the packet

        :return: The x-coordinate of the chip, between 0 and 255
        :rtype: int
        """
        return self._destination_chip_x

    @destination_chip_x.setter
    def destination_chip_x(self, destination_chip_x):
        """ Set the x-coordinate of the destination chip of the packet

        :param destination_chip_x: The x-coordinate to set, between 0 and 255
        :type destination_chip_x: int
        :return: Nothing is returned
        :rtype: None
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If the\
                    destination_chip_x has already been set or if the value is\
                    out of range
        """
        if self._destination_chip_x is not None:
            raise SpinnmanInvalidParameterException(
                "destination_chip_x", str(destination_chip_x),
                "Already set")
        if destination_chip_x is not None and (destination_chip_x < 0
                                               or destination_chip_x > 255):
            raise SpinnmanInvalidParameterException(
                "destination_chip_x", str(destination_chip_x),
                "Must be between 0 and 255")

        self._destination_chip_x = destination_chip_x

    @property
    def destination_chip_y(self):
        """ The y-coordinate of the destination chip of the packet

        :return: The y-coordinate of the chip, between 0 and 255
        :rtype: int
        """
        return self._destination_chip_y

    @destination_chip_y.setter
    def destination_chip_y(self, destination_chip_y):
        """ Set the y-coordinate of the destination chip of the packet

        :param destination_chip_y: The y-coordinate to set, between 0 and 255
        :type destination_chip_y: int
        :return: Nothing is returned
        :rtype: None
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If the\
                    destination_chip_y has already been set or if the value is\
                    out of range
        """
        if self._destination_chip_y is not None:
            raise SpinnmanInvalidParameterException(
                "destination_chip_y", str(destination_chip_y),
                "Already set")
        if destination_chip_y is not None and (destination_chip_y < 0
                                               or destination_chip_y > 255):
            raise SpinnmanInvalidParameterException(
                "destination_chip_y", str(destination_chip_y),
                "Must be between 0 and 255")

        self._destination_chip_y = destination_chip_y

    @property
    def source_port(self):
        """ The source port of the packet

        :return: The source port of the packet between 0 and 7
        :rtype: int
        """
        return self._source_port

    @source_port.setter
    def source_port(self, source_port):
        """ Set the source port of the packet

        :param source_port: The source port to set, between 0 and 7
        :type source_port: int
        :return: Nothing is returned
        :rtype: None
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If the\
                    source_port has already been set or if the value is out of\
                    range
        """
        if self._source_port is not None:
            raise SpinnmanInvalidParameterException(
                "source_port", str(source_port), "Already set")
        if source_port is not None and (source_port < 0 or source_port > 7):
            raise SpinnmanInvalidParameterException(
                "source_port", str(source_port), "Must be between 0 and 7")

        self._source_port = source_port

    @property
    def source_cpu(self):
        """ The core on the source chip

        :return: The core on the source chip, between 0 and 31
        :rtype: int
        """
        return self._source_cpu

    @source_cpu.setter
    def source_cpu(self, source_cpu):
        """ Set the id of the source processor of the packet

        :param source_cpu: The processor id to set, between 0 and 31
        :type source_cpu: int
        :return: Nothing is returned
        :rtype: None
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If the\
                    source_cpu has already been set or if the value is out\
                    of range
        """
        if self._source_cpu is not None:
            raise SpinnmanInvalidParameterException(
                "source_cpu", str(source_cpu), "Already set")
        if source_cpu is not None and (source_cpu < 0 or source_cpu > 31):
            raise SpinnmanInvalidParameterException(
                "source_cpu", str(source_cpu), "Must be between 0 and 31")

        self._source_cpu = source_cpu

    @property
    def source_chip_x(self):
        """ The x-coordinate of the source chip of the packet

        :return: The x-coordinate of the chip, between 0 and 255
        :rtype: int
        """
        return self._source_chip_x

    @source_chip_x.setter
    def source_chip_x(self, source_chip_x):
        """ Set the x-coordinate of the source chip of the packet

        :param source_chip_x: The x-coordinate to set, between 0 and 255
        :type source_chip_x: int
        :return: Nothing is returned
        :rtype: None
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If the\
                    source_chip_x has already been set or if the value is out\
                    of range
        """
        if self._source_chip_x is not None:
            raise SpinnmanInvalidParameterException(
                "source_chip_x", str(source_chip_x), "Already set")
        if source_chip_x is not None and (source_chip_x < 0
                                          or source_chip_x > 255):
            raise SpinnmanInvalidParameterException(
                "source_chip_x", str(source_chip_x),
                "Must be between 0 and 255")

        self._source_chip_x = source_chip_x

    @property
    def source_chip_y(self):
        """ The y-coordinate of the source chip of the packet

        :return: The y-coordinate of the chip, between 0 and 255
        :rtype: int
        """
        return self._source_chip_y

    @source_chip_y.setter
    def source_chip_y(self, source_chip_y):
        """ Set the y-coordinate of the source chip of the packet

        :param source_chip_y: The y-coordinate to set, between 0 and 255
        :type source_chip_y: int
        :return: Nothing is returned
        :rtype: None
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If the\
                    source_chip_y has already been set or if the value is out\
                    of range
        """
        if self._source_chip_y is not None:
            raise SpinnmanInvalidParameterException(
                "source_chip_y", str(source_chip_y), "Already set")
        if source_chip_y is not None and (source_chip_y < 0
                                          or source_chip_y > 255):
            raise SpinnmanInvalidParameterException(
                "source_chip_y", str(source_chip_y),
                "Must be between 0 and 255")

        self._source_chip_y = source_chip_y

    def write_sdp_header(self, byte_writer):
        """ Write the SDP header to a byte_writer

        :param byte_writer: The writer to write the data to
        :type byte_writer:\
                    :py:class:`spinnman.data.abstract_byte_writer.AbstractByteWriter`
        :return: Nothing is returned
        :rtype: None
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    writing to the writer
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If any\
                    of the parameter values have not been set
        """
        if self._flags is None:
            raise SpinnmanInvalidParameterException(
                "sdp_header.flags", str(None), "No value has been assigned")
        if self._tag is None:
            raise SpinnmanInvalidParameterException(
                "sdp_header.tag", str(None), "No value has been assigned")
        if self._destination_port is None:
            raise SpinnmanInvalidParameterException(
                "sdp_header.destination_port", str(None),
                "No value has been assigned")
        if self._destination_cpu is None:
            raise SpinnmanInvalidParameterException(
                "sdp_header.destination_cpu", str(None),
                "No value has been assigned")
        if self._destination_chip_x is None:
            raise SpinnmanInvalidParameterException(
                "sdp_header.destination_chip_x", str(None),
                "No value has been assigned")
        if self._destination_chip_y is None:
            raise SpinnmanInvalidParameterException(
                "sdp_header.destination_chip_y", str(None),
                "No value has been assigned")
        if self._source_port is None:
            raise SpinnmanInvalidParameterException(
                "sdp_header.source_port", str(None),
                "No value has been assigned")
        if self._source_cpu is None:
            raise SpinnmanInvalidParameterException(
                "sdp_header.source_cpu", str(None),
                "No value has been assigned")
        if self._source_chip_x is None:
            raise SpinnmanInvalidParameterException(
                "sdp_header.source_chip_x", str(None),
                "No value has been assigned")
        if self._source_chip_y is None:
            raise SpinnmanInvalidParameterException(
                "sdp_header.source_chip_y", str(None),
                "No value has been assigned")

        try:
            byte_writer.write_byte(self._flags.value)
            byte_writer.write_byte(self._tag)
            byte_writer.write_byte(((self._destination_port & 0x7) << 5) |
                                   (self._destination_cpu & 0x1F))
            byte_writer.write_byte(((self._source_port & 0x7) << 5) |
                                   (self._source_cpu & 0x1F))
            byte_writer.write_byte(self._destination_chip_y)
            byte_writer.write_byte(self._destination_chip_x)
            byte_writer.write_byte(self._source_chip_y)
            byte_writer.write_byte(self._source_chip_x)
        except IOError as exception:
            raise SpinnmanIOException(str(exception))

    def read_sdp_header(self, byte_reader):
        """ Read an SDP header from a byte_reader

        :param byte_reader: The reader to read the data from
        :type byte_reader:\
                    :py:class:`spinnman.data.abstract_byte_reader.AbstractByteReader`
        :return: Nothing is returned
        :rtype: None
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    reading from the reader
        :raise spinnman.exceptions.SpinnmanInvalidPacketException: If there\
                    are too few bytes to read the header
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If there\
                    is an error setting any of the values
        """
        flags_value = None
        try:
            flags_value = byte_reader.read_byte()
            self.flags = SDPFlag(flags_value)
            self.tag = byte_reader.read_byte()
            destination_values = byte_reader.read_byte()
            self.destination_port = (destination_values >> 5) & 0x7
            self.destination_cpu = destination_values & 0x1F
            source_values = byte_reader.read_byte()
            self.source_port = (source_values >> 5) & 0x7
            self.source_cpu = source_values & 0x1F
            self.destination_chip_y = byte_reader.read_byte()
            self.destination_chip_x = byte_reader.read_byte()
            self.source_chip_y = byte_reader.read_byte()
            self.source_chip_x = byte_reader.read_byte()
        except ValueError as exception:
            raise SpinnmanInvalidParameterException(
                "flags", flags_value,
                "Unrecognized value")
        except IOError as exception:
            raise SpinnmanIOException(str(exception))
        except EOFError as exception:
            raise SpinnmanInvalidPacketException(
                "SDP (header)",
                "Not enough bytes to read a header")