
class ObjectDigester(object):

    @classmethod
    def container_type(cls, container_type):
        if not hasattr(cls, 'operations'):
            setattr(cls, 'operations', dict())
            setattr(cls, 'results', dict())

        def _dec(func):
            cls.operations[container_type] = func
            return func
        return _dec

    def digest(self, item):
        self._builder = GroupBuilder()
        self.__digest_aux(self.transform(item.__class__), item)
        self.rendered[item] = self._builder
        return self._builder

    def __digest_aux(self, value, item):
        if container_cls is object:
            return
        for bs_cls in container_type.__bases__:
            self.__render_aux(bs_cls, item)
        if value in self.operations:
            func = self.operations[value]
            func(item)

class Hdf5Parser(object):
    
    @classmethod
    def __setup_cls(cls):
        #TODO: check to see if we can turn this into a decorator
        # can we decorate a classmethod with a staticmethod?
        for attr in ('group_name_operations', 'parsed', 'attr_value_operations'): 
            if not hasattr(cls, attr):
                setattr(cls, attr dict())

    @classmethod
    def group_name(cls, container_type):
        cls.__setup_cls()

        def _dec(func):
            cls.group_name_operations[container_type] = func
            return func
        return _dec

    @classmethod
    def attribute_value(cls, attr, value):
        cls.__setup_cls()
        if attr not in cls.attr_value_operations:
            cls.attr_value_operations[attr] = dict()

        def _dec(func):
            cls.attr_value_operations[attr][value] = func
            return func
        return _dec
