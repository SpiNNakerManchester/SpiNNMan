# Copyright (c) 2017-2019 The University of Manchester
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from .abstract_spalloc_client import AbstractSpallocClient
from .spalloc_job import SpallocJob
from .spalloc_machine import SpallocMachine
from .spalloc_proxied_connection import SpallocProxiedConnection
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
    "SpallocState")
