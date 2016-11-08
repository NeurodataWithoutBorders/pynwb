import abc as _abc

class ExtenderMeta(_abc.ABCMeta):
    """A metaclass that will extend the base class initialization
       routine by executing additional functions defined in 
       classes that use this metaclass
        
       In general, you should not use this class, unless your name is
       Andrew James Tritt.
    """

    __postinit = '__postinit'
    def post_init(func):
        print("setting __post_definition__ in %s" % str(func))
        setattr(func, MyMeta.__postinit, True)
        return classmethod(func)

    def __init__(cls, name, bases, classdict):
        super(MyMeta, cls).__init__(name, bases, classdict)
        it = (getattr(cls, n) for n in dir(cls))
        it = (a for a in it if hasattr(a, MyMeta.__postinit))
        for func in it:
            func()

class BaseObjectHandler(object, metaclass=ExtenderMeta):

    __property = "__item_property__"
    @ExtenderMeta.post_init
    def __gather_procedures(cls):
        cls.procedures = dict()
        for name, func in filter(lambda tup: hasattr(tup[1], cls.__property), cls.__dict__.items()):
            # NOTE: We need to get the original functions from the class dict since
            # the attributes added to cls after calling type will be processed. 
            # i.e. staticmethod objects lose their attributes in the binding process
            # But, we need to get the function after it's been bound, since
            # staticmethod objects are not callable (after staticmethods are processed
            # by type, they are bound to the class as a function)
            cls.procedures[getattr(func, cls.__property)] = getattr(cls, name)
    

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
    def procedure(cls, prop):
        """Decorator for adding procedures within definition
           of derived classes.
        """
        def _dec(func):
            func2 = staticmethod(func)
            setattr(func2, MyBaseClass.__property, prop)
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

