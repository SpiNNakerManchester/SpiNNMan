__author__ = 'stokesa6'
import struct
from spinnman import exceptions


class _SDPMessage(object):
    """Wraps up an SDP message that may be sent or received to/from a SpiNNaker\
       using a :py:class:`SDPConnection`.\
    \
    Typical usage:: \
    \
        conn         = SDPConnection ('fiercebeast2', 17892)\
        msg          = SDPMessage ()\
        msg.dst_cpu  = 1\
        msg.dst_port = 7\
        msg.data     = "Hello!"\
        conn.send (msg)\
    \
    Only a small number of fields are used for SDP messages:\
    \
        ``flags`` (8 bits)\
            Amongst other things, determines whether the packet commands a\
            response or not\
    \
        ``tag`` (8 bits)\
            IP tag to use, or the IP used.\
    \
        ``dst_cpu`` (5 bits)\
            Target processor on target node (0-17)\
    \
        ``dst_port`` (3 bits)\
            Port on target processor (0-7)\
    \
        ``src_cpu`` (5 bits)\
            Originating processor on source node (0-17)\
    \
        ``src_port`` (3 bits)\
            Port on source processor (0-7)\
    \
        ``dst_x`` and ``dst_y`` (both 8 bits)\
            (X, Y) co-ordinates of target node\
    \
        ``src_x`` and ``src_y`` (both 8 bits)\
            (X, Y) co-ordinates of initiating node\
    \
        ``data`` (variable length)\
            Up to 272 bytes of payload data\
    \
    .. note::\
    \
        Although :class:`SDPMessage` is typically used in conjunction with the\
        :class:`SDPConnection` class, this is not a requirement.  Calling\
        :func:`str` on an :class:`SDPMessage` object will encode the contents\
        as a string, and calling :py:meth:`~SDPMessage.from_string` will \
        perform the reverse.
    """

    def __init__(self, packed=None, **kwargs):
        """Constructs a new :py:class:`SDPMessage` object with either default\
           values or those provided.\
        \
        .. note::\
            If neither ``packed`` nor ``kwargs`` are provided than internal\
            default values will be used.

        :param packed: encoded packet data
        :type packed:  string or None
        :param kwargs: keyword arguments providing initial values
        :type: kwargs: dict
        :return: a new SDP_message object
        :rtype: spinnman.sdp.sdp_message.SdpMessage object
        :raise None: does not raise any known exceptions
        """
        # sizeof(sdp_hdr_t) == 8 in SC&MP/SARK -- used for the size calculation
        self._sizeof_hdr = 8

        if packed is not None:
            self.from_string(packed)
        else:
            self.flags = 0x87
            self.tag = 0xFF
            self.dst_cpu = 0
            self.dst_port = 1
            self.src_cpu = 31
            self.src_port = 7
            self.dst_x = 0
            self.dst_y = 0
            self.src_x = 0
            self.src_y = 0
            self.data = ''

        # use given values if possible
        if kwargs:
            self.from_dict(kwargs)

    def _pack_hdr(self):
        """Constructs a string containing *only* the SDP header.

        :return: header encoded as a string
        :rtype: str
        :raise None: does not raise any known exceptions
        """
        # generate source and destination addresses
        src_proc = ((self.src_port & 7) << 5) | (self.src_cpu & 31)
        dst_proc = ((self.dst_port & 7) << 5) | (self.dst_cpu & 31)
        src_addr = ((self.src_x & 0xFF) << 8) | (self.src_y & 0xFF)
        dst_addr = ((self.dst_x & 0xFF) << 8) | (self.dst_y & 0xFF)

        # pack the header
        return struct.pack('< 6B 2H', 8, 0, self.flags, self.tag, dst_proc,
                           src_proc, dst_addr, src_addr)

    def __str__(self):
        """Constructs a string that can be sent over a network socket using the
           member variables.

        :return: encoded string
        :rtype: str
        :raise None: does not raise any known exceptions
        """
        return self._pack_hdr() + self.data

    def __len__(self):
        """Determines the length of the SDP message represented by this class.

        :return: length of the data in this object
        :rtype: int
        :raise None: does not raise any known exceptions
        """
        return self._sizeof_hdr + len(self.data)

    @staticmethod
    def _unpack_hdr(packed):
        """Reconstructs only an SDP header from ``packed`` and return what is
           assumed to be payload.

        :param packed: packed data to decode
        :type packed: str
        :return: dictionary of header fields, payload array
        :rtype: dict
        :raise None: does not raise any known exceptions
        """
        # divide the data into the header and the payload
        pkt, header, payload = {}, packed[:10], packed[10:]

        # unpack the header
        (pkt['flags'], pkt['tag'], dst_proc, src_proc, dst_addr,
            src_addr) = struct.unpack('< 2x 4B 2H', header)

        # unmap the tightly packed bits
        pkt['src_port'], pkt['src_cpu'] = src_proc >> 5, src_proc & 0x1F
        pkt['dst_port'], pkt['dst_cpu'] = dst_proc >> 5, dst_proc & 0x1F
        pkt['src_x'],    pkt['src_y'] = src_addr >> 8, src_addr & 0xFF
        pkt['dst_x'],    pkt['dst_y'] = dst_addr >> 8, dst_addr & 0xFF

        # return the unpacked header and the payload
        return pkt, payload

    def from_string(self, packed):
        """Deconstructs the given string and sets the member
           variables accordingly.
           
        :param packed: packed data to decode
        :type packed: str
        :return: None
        :rtype: None
        :raise spinnman.exceptions.SpinnmanStructInterpertationException: \
                            when the struct module cannot unpack the packed\
                            data
        """
        try:
            # unpack the header and the payload
            hdr, payload = self._unpack_hdr(packed)
        except struct.error:
            raise exceptions.\
                SpinnmanStructInterpertationException("could not interperate "
                                                      "the data contained "
                                                      "within {} when "
                                                      "generating a sdp message"
                                                      .format(packed))
        # merge the fields and store the payload
        self.from_dict(hdr)
        self.data = payload

    def from_dict(self, sdp_fields):
        """Updates the SDPMessage object from the given key-value map of valid
           fields.

        :param sdp_fields: valid SDP fields
        :type sdp_fields: dict
        :return: None
        :rtype: None
        :raise Spinnman.exceptions.SpinnmanunrecogonisedAttributeException: \
                         when an parameter in sdp_fields is not a recogonised \
                         parameter of a sdp_message
        """
        k, v = None
        try:
            for k, v in sdp_fields.iteritems():
                setattr(self, k, v)
        except AttributeError:
            raise exceptions.\
                SpinnmanUnrecogonisedAttributeException("The attribute {} was"
                                                        " not recognised as a "
                                                        "attribute of a SDP "
                                                        "message".format(k))
