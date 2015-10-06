
from abc import ABCMeta
from six import add_metaclass


@add_metaclass(ABCMeta)
class AbstractEIEIOMessage(object):
    """ Marker interface for an EIEIOMessage
    """
