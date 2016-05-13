from spinnman.model.cpu_state import CPUState
import struct


class ChipSummaryInfo(object):
    """ Represents the chip summary information read via an SCP command
    """

    def __init__(self, chip_summary_data, offset, x=None, y=None):
        """
        :param chip_summary_data: The data from the SCP response
        :type: chip_summary_data: bytearray
        :param offset: The offset into the data where the data starts
        :type offset: int
        :param x: The x-coordinate of the chip that this data is from;\
                required if the version of the data is 0
        :param y: The y-coordinate of the chip that this data is from;\
                required if the version of the data is 0
        """
        (chip_summary_flags, self._largest_free_sdram_block,
            self._largest_free_sdram_block) = struct.unpack_from(
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

        # The following items are only included if the version is 1
        self._link_destinations = None
        self._x = None
        self._y = None
        self._vcpu_base_address = None
        self._multicast_routes_copy_address = None
        self._fixed_route_copy_address = None
        self._nearest_ethernet_x = None
        self._nearest_ethernet_y = None
        self._cpu_speed_mhz = None
        self._ethernet_ip_address = None
        self._width = None
        self._height = None

        # If the version is 0, the x and y must be provided
        self._version = (chip_summary_flags >> 26) & 0x1
        if self._version == 0 and (x is None or y is None):
            raise Exception(
                "x and y must be specified if version 0 data is used")
        if self._version == 0:
            self._x = x
            self._y = y

        # The remaining items are only available if specified
        if self._version == 1:
            (link_p2p_ids, self._y, self._x, self._vcpu_base_address,
                self._multicast_routes_copy_address,
                self._fixed_route_copy_address,
                self._nearest_ethernet_y, self._nearest_ethernet_x,
                self._cpu_speed_mhz) = struct.unpack_from(
                    "<12s2B3I2BH", chip_summary_data, data_offset)
            data_offset += 30

            link_p2p_ids = bytearray(link_p2p_ids)
            self._link_destinations = {
                i: (link_p2p_ids[(i * 2) + 1], link_p2p_ids[i * 2])
                for i in self._working_links}

            # The Ethernet address is only available if the Ethernet is
            # available
            if self._is_ethernet_available:
                ip_data = struct.unpack_from(
                    "<4B", chip_summary_data, data_offset)
                self._ethernet_ip_address = "{}.{}.{}.{}".format(
                    ip_data[0], ip_data[1], ip_data[2], ip_data[3])
                data_offset += 4

            # The size of the machine is only available if bit 27 is 1
            if (chip_summary_flags & (1 << 27)) != 0:
                self._height, self._width = struct.unpack_from(
                    "<BB", chip_summary_data, data_offset)

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
    def version(self):
        """ The version of the data - if 0, only contains:
            n_cores, core_states, is_ethernet_available,
            largest_free_sdram_block, largest_free_sram_block,
            n_free_multicast_routing_entries and working links
        """
        return self._version

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

    def get_link_destination(self, link):
        """ Get the x and y coordinates of the chip down the given link, or\
            None if the link is not working

        :param link: The id of the link to find the destination of
        :rtype: (int, int) or None
        """
        if link not in self._link_destinations:
            return None
        return self._link_destinations[link]

    @property
    def vcpu_base_address(self):
        """ The address of the VCPU structure on the chip

        :rtype: int
        """
        return self._vcpu_base_address

    @property
    def multicast_routes_copy_address(self):
        """ The address of the copy of the multicast routes

        :rtype: int
        """
        return self._multicast_routes_copy_address

    @property
    def fixed_route_copy_address(self):
        """ The address of the copy of the fixed route

        :rtype: int
        """
        return self._fixed_route_copy_address

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
    def cpu_speed_mhz(self):
        """ The speed of the CPUs in MHz

        :rtype: int
        """
        return self._cpu_speed_mhz

    @property
    def ethernet_ip_address(self):
        """ The IP address of the Ethernet if up, or None if not

        :rtype: str
        """
        return self._ethernet_ip_address

    @property
    def width(self):
        """ The width of the machine, if requested, or None if not

        :rtype: int
        """
        return self._width

    @property
    def height(self):
        """ The height of the machine, if requested, or None if not

        :rtype: int
        """
        return self._height
