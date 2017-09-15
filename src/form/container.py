import abc
from six import with_metaclass

class Container(with_metaclass(abc.ABCMeta, object)):

    @classmethod
    def type_hierarchy(cls):
        return cls.__mro__
