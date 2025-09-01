# Copyright (c) 2025 The University of Manchester
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

from typing import Optional, Type

from spinn_utilities.config_holder import load_config
from spinnman.data.spinnman_data_writer import SpiNNManDataWriter


class SpiNNManSimulation(object):
    """
    The SpiNNMan level part of the simulation interface.
    """

    __slots__ = (
        # The writer and therefore view of the global data
        "_data_writer", )


    def __init__(
            self, data_writer_cls: Optional[Type[SpiNNManDataWriter]] = None):
        load_config()

        if data_writer_cls:
            self._data_writer = data_writer_cls.setup()
        else:
            self._data_writer = SpiNNManDataWriter.setup()

