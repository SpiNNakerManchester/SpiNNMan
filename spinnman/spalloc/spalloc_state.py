# Copyright (c) 2014-2023 The University of Manchester
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from enum import IntEnum


class SpallocState(IntEnum):
    #: The job is in an unknown state.
    UNKNOWN = 0
    #: The job is queued waiting for allocation.
    QUEUED = 1
    #: The job is queued waiting for boards to power on or off.
    POWER = 2
    #: The job is ready for user code to run on it.
    READY = 3
    #: The job has been destroyed.
    DESTROYED = 4
