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
from __future__ import annotations
from enum import Enum
from typing import FrozenSet, Sequence
from spinnman.model.enums import CPUState


class ExecutableType(Enum):
    """
    The different types of executable from the perspective of how they
    are started and controlled.
    """
    value: int
    start_state: FrozenSet[CPUState]
    end_state: FrozenSet[CPUState]
    supports_auto_pause_and_resume: bool

    #: Runs immediately without waiting for barrier and then exits.
    RUNNING = (
        0,
        [CPUState.RUNNING],
        [CPUState.FINISHED],
        False,
        "Runs immediately without waiting for barrier and then exits")
    #: Calls ``spin1_start(SYNC_WAIT)`` and then eventually ``spin1_exit()``.
    SYNC = (
        1,
        [CPUState.SYNC0],
        [CPUState.FINISHED],
        False,
        "Calls spin1_start(SYNC_WAIT) and then eventually spin1_exit()")
    #: Calls ``simulation_run()`` and ``simulation_exit()`` /
    #: ``simulation_handle_pause_resume()``.
    USES_SIMULATION_INTERFACE = (
        2,
        [CPUState.SYNC0, CPUState.SYNC1, CPUState.PAUSED, CPUState.READY],
        [CPUState.READY],
        True,
        "Calls simulation_run() and simulation_exit() / "
        "simulation_handle_pause_resume()")
    #: Situation where there user has supplied no application but for some
    #: reason still wants to run.
    NO_APPLICATION = (
        3,
        (),
        (),
        True,
        "Situation where there user has supplied no application but for "
        "some reason still wants to run")
    #: Runs immediately without waiting for barrier and never ends.
    SYSTEM = (
        4,
        [CPUState.RUNNING],
        [CPUState.RUNNING],
        True,
        "Runs immediately without waiting for barrier and never ends")

    def __new__(cls, value: int, start_state: Sequence[CPUState],
                end_state: Sequence[CPUState],
                supports_auto_pause_and_resume: bool,
                doc: str = "") -> 'ExecutableType':
        obj = object.__new__(cls)
        obj._value_ = value
        obj. __doc__ = doc
        return obj

    def __init__(self, value: int, start_state: Sequence[CPUState],
                 end_state: Sequence[CPUState],
                 supports_auto_pause_and_resume: bool, doc: str = ""):
        """
        :param value: ID for the enum
        :param start_state: The state(s) this type could start in
        :param end_state: The state(s) this type will be in at the end
        :param supports_auto_pause_and_resume: Flag to say this type can run
           when the run is split into smaller blocks
        :param doc: Description of the type
        """
        _ = (value, doc)
        self.start_state: FrozenSet[CPUState] = frozenset(start_state)
        self.end_state: FrozenSet[CPUState] = frozenset(end_state)
        self.supports_auto_pause_and_resume = supports_auto_pause_and_resume
