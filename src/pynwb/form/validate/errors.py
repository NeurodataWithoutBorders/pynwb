
from ..utils import docval, getargs

__all__ = [
    "Error",
    "DtypeError",
    "MissingError",
    "ShapeError",
    "MissingDataType",
]


class Error(object):

    @docval({'name': 'name', 'type': str, 'doc': 'the name of the component that is erroneous'},
            {'name': 'reason', 'type': str, 'doc': 'the reason for the error'})
    def __init__(self, **kwargs):
        self.__name = getargs('name', kwargs)
        self.__reason = getargs('reason', kwargs)

    @property
    def name(self):
        return self.__name

    @property
    def reason(self):
        return self.__reason

    def __str__(self):
        return "%s - %s: %s" % (self.__class__.__name__, self.name, self.reason)

    def __repr__(self):
        return self.__str__()


class DtypeError(Error):

    @docval({'name': 'name', 'type': str, 'doc': 'the name of the component that is erroneous'},
            {'name': 'expected', 'type': (type, str), 'doc': 'the expected dtype'},
            {'name': 'received', 'type': (type, str), 'doc': 'the received dtype'})
    def __init__(self, **kwargs):
        name = getargs('name', kwargs)
        expected = getargs('expected', kwargs)
        received = getargs('received', kwargs)
        reason = "incorrect type: expected '%s', got'%s'" % (expected, received)
        super(DtypeError, self).__init__(name, reason)


class MissingError(Error):
    @docval({'name': 'name', 'type': str, 'doc': 'the name of the component that is erroneous'})
    def __init__(self, **kwargs):
        name = getargs('name', kwargs)
        reason = "argument missing"
        super(MissingError, self).__init__(name, reason)


class MissingDataType(Error):
    @docval({'name': 'name', 'type': str, 'doc': 'the name of the component that is erroneous'},
            {'name': 'data_type', 'type': str, 'doc': 'the missing data type'})
    def __init__(self, **kwargs):
        name, data_type = getargs('name', 'data_type', kwargs)
        self.__data_type = data_type
        reason = "missing data type %s" % self.__data_type
        super(MissingDataType, self).__init__(name, reason)

    @property
    def data_type(self):
        return self.__data_type


class ShapeError(object):

    @docval({'name': 'name', 'type': str, 'doc': 'the name of the component that is erroneous'},
            {'name': 'expected', 'type': (tuple, list), 'doc': 'the expected shape'},
            {'name': 'received', 'type': (tuple, list), 'doc': 'the received shape'})
    def __init__(self, **kwargs):
        name = getargs('name', kwargs)
        expected = getargs('expected', kwargs)
        received = getargs('received', kwargs)
        reason = "incorrect shape: expected '%s', got'%s'" % (expected, received)
        super(ShapeError, self).__init__(name, reason)
