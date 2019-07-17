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

_MIN_APP_ID = 17
_MAX_APP_ID = 254


class AppIdTracker(object):
    """ A tracker of application IDs to make it easier to allocate new IDs.
    """
    __slots__ = [
        "_free_ids",
        "_max_app_id",
        "_min_app_id"]

    # Keep a class-global reference to the free ID range, so IDs are
    # allocated globally

    def __init__(
            self, app_ids_in_use=None, min_app_id=_MIN_APP_ID,
            max_app_id=_MAX_APP_ID):
        """
        :param app_ids_in_use: The IDs that are already in use
        :type app_ids_in_use: list[int] or None
        :param min_app_id: The smallest application ID to use
        :type min_app_id: int
        :param max_app_id: The largest application ID to use
        :type max_app_id: int
        """
        self._free_ids = set(range(min_app_id, max_app_id))
        if app_ids_in_use is not None:
            self._free_ids.difference_update(app_ids_in_use)
        self._min_app_id = min_app_id
        self._max_app_id = max_app_id

    def get_new_id(self):
        """ Get a new unallocated ID

        :rtype: int
        """
        return self._free_ids.pop()

    def allocate_id(self, allocated_id):
        """ Allocate a given ID.

        :param allocated_id: The ID to allocate
        :raises KeyError: If the ID is not present
        """
        self._free_ids.remove(allocated_id)

    def free_id(self, id_to_free):
        """ Free a given ID.

        :param id_to_free: The ID to free
        :raises KeyError: If the ID is out of range
        """
        if id_to_free < self._min_app_id or id_to_free > self._max_app_id:
            raise KeyError("ID {} out of allowed range of {} to {}".format(
                id_to_free, self._min_app_id, self._max_app_id))
        self._free_ids.add(id_to_free)
