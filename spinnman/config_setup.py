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
from typing import Set

from spinn_utilities.config_holder import (
    add_default_cfg, clear_cfg_files, get_config_bool, get_config_str_or_none)
from spinn_utilities.configs.camel_case_config_parser import optionxform

from spinn_machine.config_setup import add_spinn_machine_cfg
from spinnman.data.spinnman_data_writer import SpiNNManDataWriter

BASE_CONFIG_FILE = "spinnman.cfg"


def unittest_setup() -> None:
    """
    Resets the configurations so only the local default configuration is
    included.

    .. note::
        This file should only be called from `SpiNNMan/unittests`.
    """
    clear_cfg_files(True)
    add_spinnman_cfg()
    SpiNNManDataWriter.mock()


def add_spinnman_cfg() -> None:
    """
    Add the local configuration and all dependent configuration files.
    """
    add_spinn_machine_cfg()  # This add its dependencies too
    add_default_cfg(os.path.join(os.path.dirname(__file__), BASE_CONFIG_FILE))


def man_cfg_paths_skipped() -> Set[str]:
    """
    cfg report options that point to paths that may not exist.

    Assuming mode = Debug

    Used in function that check reports exists at the end of a debug node run.

    :returns:
       Set of cfg path that may not be found based on other cfg settings
    """
    skipped = set()
    if get_config_bool("Machine", "virtual_board"):
        skipped.add(optionxform("path_ignores_report"))
    if (not get_config_str_or_none("Machine", "down_cores") and
            not get_config_str_or_none("Machine", "down_chips") and
            not get_config_str_or_none("Machine", "down_links")):
        skipped.add(optionxform("path_ignores_report"))
    return skipped
