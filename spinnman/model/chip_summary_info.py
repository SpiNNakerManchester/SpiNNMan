import struct

from spinnman.model.enums import CPUState


class ChipSummaryInfo(object):
    """ Represents the chip summary information read via an SCP command
    """

    def __init__(self, chip_summary_data, offset, x, y):
        """
        :param chip_summary_data: The data from the SCP response
        :type chip_summary_data: bytearray
        :param offset: The offset into the data where the data starts
        :type offset: int
        :param x: The x-coordinate of the chip that this data is from
        :param y: The y-coordinate of the chip that this data is from
        """
        (chip_summary_flags, self._largest_free_sdram_block,
            self._largest_free_sram_block) = struct.unpack_from(
                "<3I", chip_summary_data, offset)
        self._n_cores = chip_summary_flags & 0x1F
        self._working_links = [
            link for link in range(0, 6)
            if chip_summary_flags >> (8 + link) & 1 != 0]
        self._n_free_multicast_routing_entries = \
            (chip_summary_flags >> 14) & 0x7FF
        self._is_ethernet_available = bool(chip_summary_flags & (1 << 25))

        data_offset = offset + 12
        self._core_states = [
            CPUState(state) for state in
            struct.unpack_from("<18B", chip_summary_data, data_offset)]
        data_offset += 18

        self._x = x
        self._y = y

        self._nearest_ethernet_x = None
        self._nearest_ethernet_y = None
        self._ethernet_ip_address = None

        (self._nearest_ethernet_y, self._nearest_ethernet_x) = \
            struct.unpack_from(
                "<BB", chip_summary_data, data_offset)
        data_offset += 2

        ip_data = struct.unpack_from(
            "<4B", chip_summary_data, data_offset)
        ethernet_ip_address = "{}.{}.{}.{}".format(
            ip_data[0], ip_data[1], ip_data[2], ip_data[3])
        if self._is_ethernet_available:
            self._ethernet_ip_address = ethernet_ip_address
        data_offset += 4

    @property
    def x(self):
        """ The x-coordinate of the chip that this data is from

        :rtype: int
        """
        return self._x

    @property
    def y(self):
        """ The y-coordinate of the chip that this data is from

        :rtype: int
        """
        return self._y

    @property
    def n_cores(self):
        """ The number of cores working on the chip (including monitors)

        :rtype: int
        """
        return self._n_cores

    @property
    def core_states(self):
        """ The state of the cores on the chip (list of one per core)

        :rtype: list of `py:class:spinnman.model.cpu_state.CPUState`
        """
        return self._core_states

    @property
    def working_links(self):
        """ The ids of the working links outgoing from this chip

        :rtype: list of int
        """
        return self._working_links

    @property
    def is_ethernet_available(self):
        """ Determines if the Ethernet connection is available on this chip

        :rtype: bool
        """
        return self._is_ethernet_available

    @property
    def n_free_multicast_routing_entries(self):
        """ The number of multicast routing entries free on this chip

        :rtype: int
        """
        return self._n_free_multicast_routing_entries

    @property
    def largest_free_sdram_block(self):
        """ The size of the largest block of free SDRAM in bytes

        :rtype: int
        """
        return self._largest_free_sdram_block

    @property
    def largest_free_sram_block(self):
        """ The size of the largest block of free SRAM in bytes

        :rtype: int
        """
        return self._largest_free_sram_block

    @property
    def nearest_ethernet_x(self):
        """ The x coordinate of the nearest Ethernet chip

        :rtype: int
        """
        return self._nearest_ethernet_x

    @property
    def nearest_ethernet_y(self):
        """ The y coordinate of the nearest Ethernet chip

        :rtype: int
        """
        return self._nearest_ethernet_y

    @property
    def ethernet_ip_address(self):
        """ The IP address of the Ethernet if up, or None if not

        :rtype: str
        """
        return self._ethernet_ip_address
