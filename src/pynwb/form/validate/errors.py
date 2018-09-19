
from ..spec.spec import DtypeHelper
from numpy import dtype


__all__ = [
    "Error",
    "DtypeError",
    "MissingError",
    "ShapeError",
    "MissingDataType",
]


class Error(object):

    def __init__(self, name, reason, location=None):
        """

        Parameters
        ----------
        name: str
            the name of the component that is erroneous
        reason: str
            the reason for the error
        location: str
            the location of the error
        """
        self.__name = name
        self.__reason = reason
        self.__location = location
        if self.__location is not None:
            self.__str = "%s (%s): %s" % (self.__name, self.__location, self.__reason)
        else:
            self.__str = "%s: %s" % (self.name, self.reason)

    @property
    def name(self):
        return self.__name

    @property
    def reason(self):
        return self.__reason

    @property
    def location(self):
        return self.__location

    @location.setter
    def location(self, loc):
        self.__location = loc
        self.__str = "%s (%s): %s" % (self.__name, self.__location, self.__reason)

    def __str__(self):
        return self.__str

    def __repr__(self):
        return self.__str__()


class DtypeError(Error):

    def __init__(self, name, expected, received, location):
        """

        Parameters
        ----------
        name: str
            the name of the component that is erroneous
        expected: dtype | type | str | list
            the expected dtype
        received: dtype | type | str | list
            the received dtype
        location: str | None, optional
            the location of the error. Default = None
        """
        name = name
        expected = expected
        received = received
        if isinstance(expected, list):
            expected = DtypeHelper.simplify_cpd_type(expected)
        reason = "incorrect type - expected '%s', got '%s'" % (expected, received)
        loc = location
        super(DtypeError, self).__init__(name, reason, location=loc)


class MissingError(Error):
    def __init__(self, name, location=None):
        """

        Parameters
        ----------
        name: str
            the name of the component that is erroneous
        location: str
            the location of the error
        """
        name = name
        reason = "argument missing"
        loc = location
        super(MissingError, self).__init__(name, reason, location=loc)


class MissingDataType(Error):
    def __init__(self, name, data_type, location=None):
        """

        Parameters
        ----------
        name: str
        data_type: str
        location: str
        """
        self.__data_type = data_type
        reason = "missing data type %s" % self.__data_type
        loc = location
        super(MissingDataType, self).__init__(name, reason, location=loc)

    @property
    def data_type(self):
        return self.__data_type


class ShapeError(Error):

    def __init__(self, name, expected, received, location=None):
        """

        Parameters
        ----------
        name: str
        expected: tuple | list
        received: tuple | list
        location: str
        kwargs
        """
        reason = "incorrect shape - expected '%s', got'%s'" % (expected, received)
        super(ShapeError, self).__init__(name, reason, location=location)
