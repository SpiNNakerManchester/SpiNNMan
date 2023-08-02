# Copyright (c) 2024 The University of Manchester
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

import logging
import struct
from spinn_utilities.abstract_base import AbstractBase, abstractmethod
from spinn_utilities.log import FormatAdapter
from spinn_utilities.logger_utils import warn_once
from spinn_utilities.require_subclass import require_subclass
from spinnman.constants import SYSTEM_VARIABLE_BASE_ADDRESS
from spinnman.data import SpiNNManDataView
from spinnman.messages.spinnaker_boot import SystemVariableDefinition
from spinnman.transceiver.abstract_transceiver import AbstractTransceiver

_ONE_BYTE = struct.Struct("B")

logger = FormatAdapter(logging.getLogger(__name__))


@require_subclass(AbstractTransceiver)
class WatchdogSetter(object, metaclass=AbstractBase):

    def __set_watch_dog_on_chip(self, x, y, watch_dog):
        """
        Enable, disable or set the value of the watch dog timer on a
        specific chip.

        .. warning::
            This method is currently deprecated and untested as there is no
            known use. Same functionality provided by ybug and bmpc.
            Retained in case needed for hardware debugging.

        :param int x: chip X coordinate to write new watchdog parameter to
        :param int y: chip Y coordinate to write new watchdog parameter to
        :param watch_dog:
            Either a boolean indicating whether to enable (True) or
            disable (False) the watchdog timer, or an int value to set the
            timer count to
        :type watch_dog: bool or int
        """
        # build what we expect it to be
        warn_once(logger, "The set_watch_dog_on_chip method is deprecated "
                          "and untested due to no known use.")
        value_to_set = watch_dog
        watchdog = SystemVariableDefinition.software_watchdog_count
        if isinstance(watch_dog, bool):
            value_to_set = watchdog.default if watch_dog else 0

        # build data holder
        data = _ONE_BYTE.pack(value_to_set)

        # write data
        address = SYSTEM_VARIABLE_BASE_ADDRESS + watchdog.offset
        self.write_memory(x=x, y=y, base_address=address, data=data)

    def set_watch_dog(self, watch_dog):
        """
        Enable, disable or set the value of the watch dog timer.

        .. warning::
            This method is currently deprecated and untested as there is no
            known use. Same functionality provided by ybug and bmpc.
            Retained in case needed for hardware debugging.

        :param watch_dog:
            Either a boolean indicating whether to enable (True) or
            disable (False) the watch dog timer, or an int value to set the
            timer count to.
        :type watch_dog: bool or int
        """
        warn_once(logger, "The set_watch_dog method is deprecated and "
                          "untested due to no known use.")
        for x, y in SpiNNManDataView.get_machine().chip_coordinates:
            self.__set_watch_dog_on_chip(x, y, watch_dog)
