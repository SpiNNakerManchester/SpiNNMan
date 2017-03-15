from six import add_metaclass

from spinn_utilities.abstract_base import AbstractBase

@add_metaclass(AbstractBase)
class AbstractEIEIOMessage(object):
    """ Marker interface for an EIEIOMessage
    """

    __slots__ = ()
