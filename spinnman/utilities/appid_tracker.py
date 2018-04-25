_MIN_APP_ID = 17
_MAX_APP_ID = 254


class AppIdTracker(object):
    """ A tracker of application IDs to make it easier to allocate new IDs.
    """
    __slots__ = [
        "_free_ids",
        "_max_app_id",
        "_min_app_id"]

    # Keep a class-global reference to the free id range, so ids are
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
