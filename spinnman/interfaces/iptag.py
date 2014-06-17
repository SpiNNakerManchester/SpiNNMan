__author__ = 'stokesa6'
from spinnman import spinnman_exceptions


class IPTag(object):
    """a class used for holding data that is contained within a IPTag"""

    def __init__(self, **kwargs):
        """Constructs an IPTag object.

        :param **kwargs: a list of elements such as 'ip', 'mac', 'port', \
                        'timeout', 'flags', 'index', 'tag', 'hostname'
        :type kwargs: dict
        :return: a IPTag object
        :rtype: spinnman.interfaces.iptag.IPTag object
        :raise: spinnman.spinnman_exceptions.InvalidIPTagConfigurationException
        """

        members = ('ip', 'mac', 'port', 'timeout', 'flags',
                   'index', 'tag', 'hostname')

        # copy the given value or default to None
        member = None
        try:
            for member in members:
                self.__dict__[member] = kwargs.setdefault(member, None)
        except Exception:
            raise spinnman_exceptions.\
                InvalidIPTagConfigurationException(" the member {} is not a "
                                                   "recognised element of a "
                                                   "IPTAG".format(member))

    def __str__(self):
        """
        Pretty print method to help in interactive mode.

        Print format:

            index: ip:port [mac]; flags, timeout

        """
        return '{:d}: {:s}:{:d} [{:s}]; {:x}, {:.02f}'\
               .format(self.__dict__['index'], self.__dict__['ip'],
                       self.__dict__['port'], self.__dict__['mac'],
                       self.__dict__['flags'],  self.__dict__['timeout'])
