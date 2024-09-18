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


class RunTimeError(Enum):
    """
    SARK Run time errors.
    """
    #: No error
    NONE = 0
    #: Branch through zero
    RESET = 1
    #: Undefined instruction
    UNDEF = 2
    #: Undefined Supervisor Call instruction or no handler
    SVC = 3
    #: Prefetch abort
    PABT = 4
    #: Data abort
    DABT = 5
    #: Unhandled interrupt request
    IRQ = 6
    #: Unhandled Fast interrupt request
    FIQ = 7
    #: Unconfigured Vectored Interrupt Controller
    VIC = 8
    #: Generic user abort
    ABORT = 9
    #: "malloc" failure
    MALLOC = 10
    #: Divide by zero
    DIVBY0 = 11
    #: Event startup failure
    EVENT = 12
    #: Fatal Software error
    SWERR = 13
    #: Failed to allocate IO buffer
    IOBUF = 14
    #: Bad event enable
    ENABLE = 15
    #: Generic null pointer error
    NULL = 16
    #: Packet startup failure
    PKT = 17
    #: Timer startup failure
    TIMER = 18
    #: API startup failure
    API = 19
    #: Sark software version conflict
    SARK_VERSRION_INCORRECT = 20
    #: Unhandled exception
    UNRECOGNISED = 99999
