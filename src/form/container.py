import abc

class Container(object, metaclass=abc.ABCMeta):

    @classmethod
    def type_hierarchy(cls):
        return cls.__mro__
