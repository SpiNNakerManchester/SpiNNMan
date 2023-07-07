# Copyright (c) 2017 The University of Manchester
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
from spinn_utilities.config_holder import (
    add_default_cfg, clear_cfg_files)
from spinn_machine.config_setup import add_spinn_machine_cfg
from spinn_machine.config_setup import setup_spin1 as machine_spin1
from spinn_machine.config_setup import setup_spin2 as machine_spin2
from spinnman.data.spinnman_data_writer import SpiNNManDataWriter

BASE_CONFIG_FILE = "spinnman.cfg"


def unittest_setup():
    """
    Resets the configurations so only the local default configuration is
    included.

    .. note::
        This file should only be called from `SpiNNMan/unittests`.
    """
    clear_cfg_files(True)
    add_spinnman_cfg()
    SpiNNManDataWriter.mock()


def add_spinnman_cfg():
    """
    Add the local configuration and all dependent configuration files.
    """
    add_spinn_machine_cfg()  # This add its dependencies too
    add_default_cfg(os.path.join(os.path.dirname(__file__), BASE_CONFIG_FILE))


def setup_spin1():
    """
    Changes any board type settings to the Values required for a Spin1 board

    :raises SpinnMachineException: If called after a Machine has been created
    """
    machine_spin1()


def setup_spin2():
    """
    Changes any board type settings to the Values required for a Spin2 board

    :raises SpinnMachineException: If called after a Machine has been created
    """
    machine_spin2()
