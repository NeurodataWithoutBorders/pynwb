from six import with_metaclass
from .core import ExtenderMeta

class Query(with_metaclass(ExtenderMeta, object)):

    __operations__ = (
        '__lt__',
        '__gt__',
        '__le__',
        '__ge__',
        '__eq__',
        '__ne__',
    )

    @classmethod
    def __build_operation(cls, op):
        def __func(self, arg):
            return cls(self, op, arg)

    @ExtenderMeta.pre_init
    def __make_operators(cls, name, bases, classdict):
        if not isinstance(cls.__operations__, tuple):
            raise TypeError("'__operations__' must be of type tuple")
        # add any new operations
        if len(bases) and 'Query' in globals() and issubclass(bases[-1], NWBContainer) \
           and bases[-1].__operations__ is not cls.__operations__:
                new_operations = list(cls.__operations__)
                new_operations[0:0] = bases[-1].__operations__
                cls.__operations__ = tuple(new_operations)
        for op in cls.__operations__:
            if not hasattr(cls, op):
                setattr(cls, op, cls.__build_operation(op))

    def __init__(self, obj, op, arg):
        self.obj = obj
        self.op = op
        self.arg = arg
        self.result = None

    def evaluate(self):
        if self.result is None:
            obj = self.obj
            if isinstance(obj, Query):
                obj = obj.evaluate()
            elif isinstance(obj, AbstractDataset):
                obj = obj.get_array()
            self.result = getattr(obj, self.op)(self.arg)
        return self.result

    def __and__(self, other):
        pass

    def __or__(self, other):
        pass

    def __xor__(self, other):
        pass

    def __contains__(self, other)
        pass


class AbstractDataset(with_metaclass(ABCMeta, object)):

    __operations__ = (
        '__lt__',
        '__gt__',
        '__le__',
        '__ge__',
        '__eq__',
        '__ne__',
    )

    @classmethod
    def __build_operation(cls, op):
        def __func(self, arg):
            return Query(self, op, arg)

    @ExtenderMeta.pre_init
    def __make_operators(cls, name, bases, classdict):
        if not isinstance(cls.__operations__, tuple):
            raise TypeError("'__operations__' must be of type tuple")
        # add any new operations
        if len(bases) and 'Query' in globals() and issubclass(bases[-1], NWBContainer) \
           and bases[-1].__operations__ is not cls.__operations__:
                new_operations = list(cls.__operations__)
                new_operations[0:0] = bases[-1].__operations__
                cls.__operations__ = tuple(new_operations)
        for op in cls.__operations__:
            if not hasattr(cls, op):
                setattr(cls, op, cls.__build_operation(op))

    @abstractmethod
    def get_array(self):
        pass

class H5Dataset(AbstractDataset):

    def get_array(self):
        if not self.cache:
            self.cache = self.data[:]
        return self.cache

