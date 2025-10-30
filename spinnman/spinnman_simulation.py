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

import logging
from typing import Type

from spinn_utilities.log import FormatAdapter
from spinn_utilities.overrides import overrides

from spinnman.config_setup import (
    add_spinnman_cfg, add_spinnman_template, SPINNMAN_CFG)
from spinnman.data.spinnman_data_writer import SpiNNManDataWriter
from .abstract_spinnman_simulation import AbstractSpiNNManSimulation

logger = FormatAdapter(logging.getLogger(__name__))


class SpiNNManSimulation(AbstractSpiNNManSimulation):
    """
    The SpiNNMan level part of the simulation interface with config info
    """

    __slots__ = ()

    @overrides(AbstractSpiNNManSimulation.add_cfg_defaults_and_template)
    def add_cfg_defaults_and_template(self) -> None:
        add_spinnman_cfg()
        add_spinnman_template()

    @property
    @overrides(AbstractSpiNNManSimulation.user_cfg_file)
    def user_cfg_file(self) -> str:
        return SPINNMAN_CFG

    @property
    @overrides(AbstractSpiNNManSimulation.data_writer_cls)
    def data_writer_cls(self) -> Type[SpiNNManDataWriter]:
        return SpiNNManDataWriter
