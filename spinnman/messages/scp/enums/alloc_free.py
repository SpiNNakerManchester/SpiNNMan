# Copyright (c) 2015 The University of Manchester
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

from enum import Enum


class AllocFree(Enum):
    """
    The SCP Allocation and Free codes.
    """
    #: Allocate SDRAM.
    ALLOC_SDRAM = 0
    #: Free SDRAM using a Pointer.
    FREE_SDRAM_BY_POINTER = 1
    #: Free SDRAM using am APP ID.
    FREE_SDRAM_BY_APP_ID = 2
    #: Allocate Routing Entries.
    ALLOC_ROUTING = 3
    #: Free Routing Entries by Pointer.
    FREE_ROUTING_BY_POINTER = 4
    #: Free Routing Entries by APP ID.
    FREE_ROUTING_BY_APP_ID = 5
