"""
BMPConnectionData
"""

class BMPConnectionData(object):
    """
    data object for whats required from a bmp connection
    """

    def __init__(self, cabinate, frame, ip_address, boards):
        self._cabinate = cabinate
        self._frame = frame
        self._ip_address = ip_address
        self._boards = boards

    @property
    def cabinate(self):
        """
        property method for cabinate
        :return:
        """
        return self._cabinate

    @property
    def frame(self):
        """
        property method for frame
        :return:
        """
        return self._frame

    @property
    def ip_address(self):
        """
        property method for ip_address
        :return:
        """
        return self._ip_address

    @property
    def boards(self):
        """
        property method for boards
        :return:
        """
        return self._boards

    def __str__(self):
        return "{}:{}:{}:{}".format(
            self._cabinate, self._frame, self._ip_address, self._boards)

    def __repr__(self):
        return self.__str__()
