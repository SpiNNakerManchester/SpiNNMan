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
import runpy
import unittest


class TestScripts(unittest.TestCase):

    def _run_script(self, script: str) -> None:
        """
        Imports/ runs a script from manual_scripts

        :param script: scrit to import/ run
        """
        this_dir = os.path.dirname(os.path.abspath(__file__))
        parent = os.path.dirname(this_dir)
        spinnman = os.path.dirname(parent)
        get_machine = os.path.join(spinnman, "manual_scripts", script)
        runpy.run_path(get_machine)

    def test_get_machine(self) -> None:
        self._run_script("get_machine.py")

    def test_get_machine_full(self) -> None:
        self._run_script("get_machine_full.py")

    def test_get_triad(self) -> None:
        self._run_script("get_triad.py")

    def test_spinnaker_start(self) -> None:
        self._run_script("spinnaker_start.py")
