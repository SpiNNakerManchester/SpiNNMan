# Copyright (c) 2014 The University of Manchester
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from spinnman.exceptions import SpinnmanInvalidParameterException
from spinnman.constants import ROUTER_REGISTER_REGISTERS
from spinnman.model.enums.router_error import RouterError


class RouterDiagnostics(object):
    """
    Represents a set of diagnostic information available from a chip router.
    """
    __slots__ = [
        "_error_status",
        "_mon",
        "_register_values",
        "_wait_1",
        "_wait_2"]

    def __init__(self, control_register, error_status, register_values):
        """
        :param int control_register: The value of the control register
        :param int error_status: The value of the error_status
        :param list(int) register_values:
            The values of the 16 router registers
        :raise SpinnmanInvalidParameterException:
            If the number of register values is not 16
        """
        if len(register_values) != 16:
            raise SpinnmanInvalidParameterException(
                "len(register_values)",
                str(len(ROUTER_REGISTER_REGISTERS)),
                "There must be exactly 16 register values")

        self._mon = (control_register >> 8) & 0x1F
        self._wait_1 = (control_register >> 16) & 0xFF
        self._wait_2 = (control_register >> 24) & 0xFF

        self._error_status = error_status

        self._register_values = register_values

    @property
    def mon(self):
        """
        The "mon" part of the control register.

        :rtype: int
        """
        return self._mon

    @property
    def wait_1(self):
        """
        The "wait_1" part of the control register.

        :rtype: int
        """
        return self._wait_1

    @property
    def wait_2(self):
        """
        The "wait_2" part of the control register.

        :rtype: int
        """
        return self._wait_2

    @property
    def error_status(self):
        """
        The error status.

        :rtype: int
        """
        return self._error_status

    @property
    def error_count(self):
        """
        The count of errors.

        :rtype: int
        """
        return self._error_status & 0xFF

    @property
    def errors_set(self):
        """
        A list of errors that have been detected.

        :rtype: list(RouterError)
        """
        return [
            error for error in RouterError if error.value & self._error_status]

    @property
    def n_local_multicast_packets(self):
        """
        The number of multicast packets received from local cores.

        :rtype: int
        """
        return self._register_values[ROUTER_REGISTER_REGISTERS.LOC_MC.value]

    @property
    def n_external_multicast_packets(self):
        """
        The number of multicast packets received from external links.

        :rtype: int
        """
        return self._register_values[ROUTER_REGISTER_REGISTERS.EXT_MC.value]

    @property
    def n_dropped_multicast_packets(self):
        """
        The number of multicast packets received that were dropped.

        :rtype: int
        """
        return self._register_values[ROUTER_REGISTER_REGISTERS.DUMP_MC.value]

    @property
    def n_local_peer_to_peer_packets(self):
        """
        The number of peer-to-peer packets received from local cores.

        :rtype: int
        """
        return self._register_values[ROUTER_REGISTER_REGISTERS.LOC_PP.value]

    @property
    def n_external_peer_to_peer_packets(self):
        """
        The number of peer-to-peer packets received from external links.

        :rtype: int
        """
        return self._register_values[ROUTER_REGISTER_REGISTERS.EXT_PP.value]

    @property
    def n_dropped_peer_to_peer_packets(self):
        """
        The number of peer-to-peer packets received that were dropped.

        :rtype: int
        """
        return self._register_values[ROUTER_REGISTER_REGISTERS.DUMP_PP.value]

    @property
    def n_local_nearest_neighbour_packets(self):
        """
        The number of nearest-neighbour packets received from local cores.

        :rtype: int
        """
        return self._register_values[ROUTER_REGISTER_REGISTERS.LOC_NN.value]

    @property
    def n_external_nearest_neighbour_packets(self):
        """
        The number of nearest-neighbour packets received from external links.

        :rtype: int
        """
        return self._register_values[ROUTER_REGISTER_REGISTERS.EXT_NN.value]

    @property
    def n_dropped_nearest_neighbour_packets(self):
        """
        The number of nearest-neighbour packets received that were dropped.

        :rtype: int
        """
        return self._register_values[ROUTER_REGISTER_REGISTERS.DUMP_NN.value]

    @property
    def n_local_fixed_route_packets(self):
        """
        The number of fixed-route packets received from local cores.

        :rtype: int
        """
        return self._register_values[ROUTER_REGISTER_REGISTERS.LOC_FR.value]

    @property
    def n_external_fixed_route_packets(self):
        """
        The number of fixed-route packets received from external links.

        :rtype: int
        """
        return self._register_values[ROUTER_REGISTER_REGISTERS.EXT_FR.value]

    @property
    def n_dropped_fixed_route_packets(self):
        """
        The number of fixed-route packets received that were dropped.

        :rtype: int
        """
        return self._register_values[ROUTER_REGISTER_REGISTERS.DUMP_FR.value]

    @property
    def user_0(self):
        """
        The number of packets counted by the user 0 router diagnostic filter.

        :rtype: int
        """
        return self._register_values[ROUTER_REGISTER_REGISTERS.USER_0.value]

    @property
    def user_1(self):
        """
        The number of packets counted by the user 1 router diagnostic filter.

        :rtype: int
        """
        return self._register_values[ROUTER_REGISTER_REGISTERS.USER_1.value]

    @property
    def user_2(self):
        """
        The number of packets counted by the user 2 router diagnostic filter.

        :rtype: int
        """
        return self._register_values[ROUTER_REGISTER_REGISTERS.USER_2.value]

    @property
    def user_3(self):
        """
        The number of packets counted by the user 3 router diagnostic filter.

        :rtype: int
        """
        return self._register_values[ROUTER_REGISTER_REGISTERS.USER_3.value]

    @property
    def user_registers(self):
        """
        The values in the user control registers.

        :return: An array of 4 values
        :rtype: list(int)
        """
        return self._register_values[
            ROUTER_REGISTER_REGISTERS.USER_0.value:
            ROUTER_REGISTER_REGISTERS.USER_3.value + 1]

    @property
    def registers(self):
        """
        The values in all of the registers.  Can be used to directly access
        the registers if they have been programmed to give different values.

        :return: An array of 16 values
        :rtype: array(int)
        """
        return self._register_values
