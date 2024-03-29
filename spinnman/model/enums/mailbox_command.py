# Copyright (c) 2014 The University of Manchester
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


class MailboxCommand(Enum):
    """
    Commands sent between an application and the monitor processor.
    """
    #: The mailbox is idle
    SHM_IDLE = 0
    #: The mailbox contains an SDP message
    SHM_MSG = 1
    #: The mailbox contains a no-operation (used for watchdog monitoring)
    SHM_NOP = 2
    #: The mailbox contains a signal
    SHM_SIGNAL = 3
    #: The mailbox contains a command
    SHM_CMD = 4
