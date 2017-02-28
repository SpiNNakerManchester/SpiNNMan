_MIN_APP_ID = 17
_MAX_APP_ID = 254


class AppIdTracker(object):
    """ A tracker of AppId to make it easier to allocate new ids
    """

    # Keep a class-global reference to the free id range, so ids are
    # allocated globally

    def __init__(
            self, app_ids_in_use=None, min_app_id=_MIN_APP_ID,
            max_app_id=_MAX_APP_ID):
        """

        :param app_ids_in_use: The ids that are already in use
        :type app_ids_in_use: list of int or None
        :param min_app_id: The smallest app id to use
        :type min_app_id: int
        :param max_app_id: The largest app id to use
        :type max_app_id: int
        """
        self._free_ids = set(range(min_app_id, max_app_id))
        if app_ids_in_use is not None:
            self._free_ids.difference_update(app_ids_in_use)
        self._min_app_id = min_app_id
        self._max_app_id = max_app_id

    def get_new_id(self):
        """ Get a new unallocated id

        :rtype: int
        """
        return self._free_ids.pop()

    def allocate_id(self, allocated_id):
        """ Allocate a given id - raises KeyError if the id is not present

        :param allocated_id: The id to allocate
        """
        self._free_ids.remove(allocated_id)

    def free_id(self, id_to_free):
        """ Free a given id - raises KeyError if the id is out of range

        :param id_to_free: The id to free
        """
        if id_to_free < self._min_app_id or id_to_free > self._max_app_id:
            raise KeyError("ID {} out of allowed range of {} to {}".format(
                id_to_free, self._min_app_id, self._max_app_id))
        self._free_ids.add(id_to_free)
