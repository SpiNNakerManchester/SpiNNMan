from spinnman.exceptions import SpinnmanInvalidParameterException
from spinnman.constants import ROUTER_REGISTER_REGISTERS


class RouterDiagnostics(object):
    """ Represents a set of diagnostic information available from a chip router
    """

    def __init__(self, control_register, error_status, register_values):
        """
        :param control_register: The value of the control register
        :type control_register: int
        :param error_status: The value of the error_status
        :type error_status: int
        :param register_values: The values of the 16 router registers
        :type register_values: iterable of int
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If the\
                    number of register values is not 16
        """
        if len(register_values) != 16:
            raise SpinnmanInvalidParameterException(
                "len(register_values)",
                str(len(ROUTER_REGISTER_REGISTERS)),
                "There must be exactly 16 register values")

        self._mon = (control_register >> 8) & 0x1F
        self._wait_1 = (control_register >> 16) & 0xFF
        self._wait_2 = (control_register >> 8) & 0xFF

        self._error_status = error_status

        self._register_values = register_values

    @property
    def mon(self):
        """ The "mon" part of the control register

        :return: The mon bits
        :rtype: int
        """
        return self._mon

    @property
    def wait_1(self):
        """ The wait_1 part of the control register

        :return: The wait_1 bits
        :rtype: int
        """
        return self._wait_1

    @property
    def wait_2(self):
        """ The wait_2 part of the control register

        :return: The wait_2 bits
        :rtype: int
        """
        return self._wait_2

    @property
    def error_status(self):
        """ The error status

        :return: The error status
        :rtype: int
        """
        return self._error_status

    @property
    def n_local_multicast_packets(self):
        """ The number of multicast packets received from local cores

        :return: The number of packets
        :rtype: int
        """
        return self._register_values[ROUTER_REGISTER_REGISTERS.LOC_MC.value]

    @property
    def n_external_multicast_packets(self):
        """ The number of multicast packets received from external links

        :return: The number of packets
        :rtype: int
        """
        return self._register_values[ROUTER_REGISTER_REGISTERS.EXT_MC.value]

    @property
    def n_dropped_multicast_packets(self):
        """ The number of multicast packets received that were dropped

        :return: The number of packets
        :rtype: int
        """
        return self._register_values[ROUTER_REGISTER_REGISTERS.DUMP_MC.value]

    @property
    def n_local_peer_to_peer_packets(self):
        """ The number of peer-to-peer packets received from local cores

        :return: The number of packets
        :rtype: int
        """
        return self._register_values[ROUTER_REGISTER_REGISTERS.LOC_PP.value]

    @property
    def n_external_peer_to_peer_packets(self):
        """ The number of peer-to-peer packets received from external links

        :return: The number of packets
        :rtype: int
        """
        return self._register_values[ROUTER_REGISTER_REGISTERS.EXT_PP.value]

    @property
    def n_dropped_peer_to_peer_packets(self):
        """ The number of peer-to-peer packets received that were dropped

        :return: The number of packets
        :rtype: int
        """
        return self._register_values[ROUTER_REGISTER_REGISTERS.DUMP_PP.value]

    @property
    def n_local_nearest_neighbour_packets(self):
        """ The number of nearest-neighbour packets received from local cores

        :return: The number of packets
        :rtype: int
        """
        return self._register_values[ROUTER_REGISTER_REGISTERS.LOC_NN.value]

    @property
    def n_external_nearest_neighbour_packets(self):
        """ The number of nearest-neighbour packets received from external\
            links

        :return: The number of packets
        :rtype: int
        """
        return self._register_values[ROUTER_REGISTER_REGISTERS.EXT_NN.value]

    @property
    def n_dropped_nearest_neighbour_packets(self):
        """ The number of nearest-neighbour packets received that were dropped

        :return: The number of packets
        :rtype: int
        """
        return self._register_values[ROUTER_REGISTER_REGISTERS.DUMP_NN.value]

    @property
    def n_local_fixed_route_packets(self):
        """ The number of fixed-route packets received from local cores

        :return: The number of packets
        :rtype: int
        """
        return self._register_values[ROUTER_REGISTER_REGISTERS.LOC_FR.value]

    @property
    def n_external_fixed_route_packets(self):
        """ The number of fixed-route packets received from external links

        :return: The number of packets
        :rtype: int
        """
        return self._register_values[ROUTER_REGISTER_REGISTERS.EXT_FR.value]

    @property
    def n_dropped_fixed_route_packets(self):
        """ The number of fixed-route packets received that were dropped

        :return: The number of packets
        :rtype: int
        """
        return self._register_values[ROUTER_REGISTER_REGISTERS.DUMP_FR.value]

    @property
    def user_0(self):
        """ the data gained from the user 0 router diag filter

        :return: the number of packets captured by this filter.
        """
        return self._register_values[ROUTER_REGISTER_REGISTERS.USER_0.value]

    @property
    def user_1(self):
        """ the data gained from the user 1 router diag filter

        :return: the number of packets captured by this filter.
        """
        return self._register_values[ROUTER_REGISTER_REGISTERS.USER_1.value]

    @property
    def user_2(self):
        """ the data gained from the user 2 router diag filter

        :return: the number of packets captured by this filter.
        """
        return self._register_values[ROUTER_REGISTER_REGISTERS.USER_2.value]

    @property
    def user_3(self):
        """ the data gained from the user 3 router diag filter

        :return: the number of packets captured by this filter.
        """
        return self._register_values[ROUTER_REGISTER_REGISTERS.USER_3.value]

    @property
    def user_registers(self):
        """ The values in the user control registers

        :return: An array of 4 values
        :rtype: array of int
        """
        return self._register_values[
            ROUTER_REGISTER_REGISTERS.USER_0.value:
            ROUTER_REGISTER_REGISTERS.USER_3.value + 1]

    @property
    def registers(self):
        """ The values in all of the registers.  Can be used to directly\
            access the registers if they have been programmed to give\
            different values

        :return: An array of 16 values
        :rtype: array of int
        """
        return self._register_values
