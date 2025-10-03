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

import importlib
import os
import pytest
import runpy
import sys
import unittest

class TestScripts(unittest.TestCase):

    def _get_script(self, script: str) -> str:
        """
        Imports/ runs a script from manual_scripts

        :param script: scrit to import/ run
        """
        this_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(this_dir)
        parent = os.path.dirname(this_dir)
        spinnman = os.path.dirname(parent)
        return os.path.join(spinnman, "manual_scripts", script)

    def _run_script(self, script: str) -> None:
        script_path = self._get_script(script)
        runpy.run_path(script_path)

    def import_from_path(self, module_name, script: str):
        script_path = self._get_script(script)
        spec = importlib.util.spec_from_file_location(module_name, script_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module

    @pytest.mark.xdist_group(name="spinnman_script")
    def test_get_machine(self) -> None:
        self._run_script("get_machine.py")

    @pytest.mark.xdist_group(name="spinnman_script")
    def test_get_machine_full(self) -> None:
        self._run_script("get_machine_full.py")

    @pytest.mark.xdist_group(name="spinnman_script")
    def test_get_triad(self) -> None:
        self._run_script("get_triad.py")

    @pytest.mark.xdist_group(name="spinnman_script")
    def test_spinnaker_start(self) -> None:
        spinnman_script = self.import_from_path("spinnman_script", "spinnaker_start.py")
        spinnman_script.run_script(save=True)
        spinnman_script.run_script(load=True)
