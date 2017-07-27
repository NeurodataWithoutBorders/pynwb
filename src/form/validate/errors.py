
from ..utils import docval, getargs

class Error(object):

    @docval({'name': 'name', 'type': str, 'doc': 'the name of the component that is erroneous'},
            {'name': 'reason', 'type': str, 'doc': 'the reason for the error'})
    def __init__(self, **kwargs):
        self.__name = getargs('name', kwargs)
        self.__reason = getargs('reason', kwargs)

    @property
    def name(self):
        return name

    @property(self):
    def reason(self):
        return self.__reason

class DtypeError(Error):

    @docval({'name': 'name', 'type': str, 'doc': 'the name of the component that is erroneous'},
            {'name': 'expected', 'type': (type, str), 'doc': 'the expected dtype'},
            {'name': 'received', 'type': (type, str), 'doc': 'the received dtype'})
    def __init__(self, **kwargs):
        name = getargs('name', kwargs)
        expected = getargs('expected', kwargs)
        received = getargs('received', kwargs)
        reason = "incorrect type: expected '%s', got'%s'" % (expected, received)
        super().__init__(name, reason)

class MissingError(Error):
    @docval({'name': 'name', 'type': str, 'doc': 'the name of the component that is erroneous'})
    def __init__(self, **kwargs):
        name = getargs('name', kwargs)
        reason = "argument missing"
        super().__init__(name, reason)

class ShapeError(object):

    @docval({'name': 'name', 'type': str, 'doc': 'the name of the component that is erroneous'},
            {'name': 'expected', 'type': (tuple, list), 'doc': 'the expected shape'},
            {'name': 'received', 'type': (tuple, list), 'doc': 'the received shape'})
    def __init__(self, **kwargs):
        name = getargs('name', kwargs)
        expected = getargs('expected', kwargs)
        received = getargs('received', kwargs)
        reason = "incorrect shape: expected '%s', got'%s'" % (expected, received)
        super().__init__(name, reason)
