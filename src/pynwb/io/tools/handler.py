from abc import abstractmethod

from pynwb.core import ExtenderMeta
from pynwb.core import docval, getargs
from collections import Iterable
import numpy as np


class BaseObjectHandler(object, metaclass=ExtenderMeta):

    _property = "__item_property__"
    @ExtenderMeta.post_init
    def __gather_procedures(cls, name, bases, classdict):
        cls.procedures = dict()
        for name, func in filter(lambda tup: hasattr(tup[1], cls._property), cls.__dict__.items()):
            # NOTE: We need to get the original functions from the class dict since
            # the attributes added to cls after calling type will be processed.
            # i.e. staticmethod objects lose their attributes in the binding process
            # But, we need to get the function after it's been bound, since
            # staticmethod objects are not callable (after staticmethods are processed
            # by type, they are bound to the class as a function)
            cls.procedures[getattr(func, cls._property)] = getattr(cls, name)

    @classmethod
    @abstractmethod
    def get_object_properties(cls, obj):
        """Defines how message properties gets extracted. This
           must be implemented in extending classes, and it
           must return a list of properties.
        """
        ...

    @classmethod
    def get_object_representation(cls, obj):
        """Defines how messages get rendered before passing them
           into procedures. By default, the object itself is returned
        """
        return obj

    def process(self, obj):
        properties = self.get_object_properties(obj)
        ret = list()
        for prop in properties:
            val = None
            if prop in self.procedures:
                func = self.procedures[prop]
                val = func(self.get_object_representation(obj))
            ret.append(val)
        return ret

    @classmethod
    def procedure(cls, prop, static=True):
        """Decorator for adding procedures within definition
           of derived classes.
        """
        def _dec(func):
            func2 = staticmethod(func) if static else func
            setattr(func2, cls._property, prop)
            return func2
        return _dec

    @classmethod
    def procedure_ext(cls, prop):
        """Decorator for adding additional procedures to
           class procedures from outside class definition.
        """
        def _dec(func):
            cls.procedures[prop] = func
            setattr(cls, func.__name__, func)
            return func
        return _dec
