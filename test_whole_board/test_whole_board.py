# Copyright (c) 2022 The University of Manchester
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

import pytest
import tempfile
import os
import traceback
import sys
import logging
from shutil import rmtree

from spinnman.exceptions import SpallocBoardUnavailableException
import spinnman.spinnman_script as sim


BOARDS = [(x, y, b) for x in range(20) for y in range(20) for b in range(3)]
SPALLOC_URL = "https://spinnaker.cs.man.ac.uk/spalloc"


@pytest.mark.parametrize("x,y,b", BOARDS)
def test_run(x, y, b):
    #set_config("Machine", "spalloc_machine", SPALLOC_MACHINE)
    test_dir = os.path.dirname(__file__)
    tmpdir = tempfile.mkdtemp(prefix=f"{x}_{y}_{b}", dir=test_dir)
    os.chdir(tmpdir)
    with open("spinnman.cfg", "w", encoding="utf-8") as f:
        f.write("[Machine]\n")
        f.write(f"spalloc_server = {SPALLOC_URL}\n")
        f.write(f"spalloc_triad = {x},{y},{b}\n")
        f.write("version = 5\n")
    try:
        sim.setup(n_boards_required=1)
        sim.get_machine()
    except SpallocBoardUnavailableException as ex:
        pytest.skip(str(ex))
    finally:
        # If no errors we will get here and we can remove the tree;
        # then only error folders will be left
        sim.end()
        rmtree(tmpdir)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main_boards = [(0, 0, 0)]
    for b_x, b_y, b_b in main_boards:
        print("", file=sys.stderr,)
        print(f"************** Testing {b_x}, {b_y}, {b_b} ******************",
              file=sys.stderr)
        try:
            test_run(b_x, b_y, b_b)
        except Exception:
            traceback.print_exc()
