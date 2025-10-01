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

import os
from typing import Optional

from spinn_utilities.config_holder import set_cfg_files

from spinn_machine import Machine

from spinnman.transceiver import Transceiver
from spinnman.spinnman_simulation import SpiNNManSimulation
from spinnman.config_setup import clear_cfg_files, add_spinnman_cfg

CONFIG_FILE_NAME = "spinnman.cfg"

__simulator: Optional[SpiNNManSimulation] = None


def setup(n_chips_required: Optional[int] = None,
          n_boards_required: Optional[int] = None) -> None:
    """
    The main method similar to PyNN setup.

    Needs to be called before any other function

    :param n_chips_required:
        Deprecated! Use n_boards_required instead.
        Must be `None` if n_boards_required specified.
    :param n_boards_required:
        if you need to be allocated a machine (for spalloc) before building
        your graph, then fill this in with a general idea of the number of
        boards you need so that the spalloc system can allocate you a machine
        big enough for your needs.
    """
    # pylint: disable=global-statement
    global __simulator
    if __simulator is not None:
        raise RuntimeError("Setup can only be called once")
    clear_cfg_files(False)
    add_spinnman_cfg()  # This add its dependencies too
    set_cfg_files(
        config_file=CONFIG_FILE_NAME,
        default=os.path.join(os.path.dirname(__file__), CONFIG_FILE_NAME))
    __simulator = SpiNNManSimulation()
    # At the moment this is done by sPyNNaker and Graph Front end
    # pylint: disable=protected-access
    __simulator._data_writer.set_n_required(
        n_boards_required, n_chips_required)


def get_machine() -> Machine:
    """
    Gets the Machine creating it if needed

    Will call get_transceiver(ensure_board_is_ready = True)

    :returns: Machine object
    """
    assert __simulator is not None
    return __simulator.get_machine()


def get_transceiver(ensure_board_is_ready: bool = True) -> Transceiver:
    """
    Gets the Transceiver creating it if needed

    :param ensure_board_is_ready:
    :return:
    """
    assert __simulator is not None
    # pylint: disable=protected-access
    return __simulator._get_transceiver(
        ensure_board_is_ready=ensure_board_is_ready)


def end() -> None:
    """
    Cleans up the machine, transceiver and spalloc objects
    """
    # pylint: disable=global-statement,protected-access
    global __simulator
    if __simulator is not None:
        __simulator._shutdown()
        __simulator = None
