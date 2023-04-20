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

"""
The new Spalloc client implementation. This has the notable distinction of
including a proxying system that allows creating a transceiver with access to
the boards of a job despite the client being not within the same firewall/NAT
security domain as the Spalloc-managed service.

The main class in here is :py:class:`~spinnman.spalloc.SpallocClient`.
"""

from .abstract_spalloc_client import AbstractSpallocClient
from .spalloc_job import SpallocJob
from .spalloc_machine import SpallocMachine
from .spalloc_proxied_connection import SpallocProxiedConnection
from .spalloc_eieio_connection import SpallocEIEIOConnection
from .spalloc_eieio_listener import SpallocEIEIOListener
from .spalloc_state import SpallocState
from .spalloc_client import SpallocClient
from .utils import is_server_address

__all__ = (
    "AbstractSpallocClient",
    "is_server_address",
    "SpallocClient",
    "SpallocJob",
    "SpallocMachine",
    "SpallocProxiedConnection",
    "SpallocEIEIOConnection",
    "SpallocEIEIOListener",
    "SpallocState")
