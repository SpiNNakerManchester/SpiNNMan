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

from enum import Enum


class MailboxCommand(Enum):
    """ Commands sent between an application and the monitor processor
    """

    SHM_IDLE = (0, "The mailbox is idle")
    SHM_MSG = (1, "The mailbox contains an SDP message")
    SHM_NOP = (2, "The mailbox contains a non-operation")
    SHM_SIGNAL = (3, "The mailbox contains a signal")
    SHM_CMD = (4, "The mailbox contains a command")

    def __new__(cls, value, doc=""):
        # pylint: disable=protected-access, unused-argument
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, value, doc=""):
        self._value_ = value
        self.__doc__ = doc
