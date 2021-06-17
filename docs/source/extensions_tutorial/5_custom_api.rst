Building a custom API for an extension
======================================

Creating custom extensions is recommended if you want a stable API that can remain the same even as you make changes
to the internal data organization. The :py:mod:`pynwb.core` module has various tools to make it easier to write
classes that behave like the rest of the PyNWB API.

The :py:mod:`pynwb.core` defines two base classes that represent the primitive structures supported by
the schema. :py:class:`~pynwb.core.NWBData` represents datasets and :py:class:`~pynwb.core.NWBContainer`
represents groups. Additionally, :py:mod:`pynwb.core` offers subclasses of these two classes for
writing classes that come with more functionality.

Docval
------
docval is a library within PyNWB and HDMF that performs input validation and automatic documentation generation. Using
the ``docval`` decorator is recommended for methods of custom API classes.

This decorator takes a list of dictionaries that specify the method parameters. These
dictionaries are used for enforcing type and building a Sphinx docstring.
The first arguments are dictionaries that specify the positional
arguments and keyword arguments of the decorated function. These dictionaries
must contain the following keys: ``'name'``, ``'type'``, and ``'doc'``. This will define a
positional argument. To define a keyword argument, specify a default value
using the key ``'default'``. To validate the dimensions of an input array
add the optional ``'shape'`` parameter.

The decorated method must take ``self`` and ``**kwargs`` as arguments.

When using this decorator, the functions :py:func:`getargs` and
:py:func:`popargs` can be used for easily extracting arguments from
kwargs.

The following code example demonstrates the use of this decorator:

.. code-block:: python

   @docval({'name': 'arg1':,   'type': str,           'doc': 'this is the first positional argument'},
           {'name': 'arg2':,   'type': int,           'doc': 'this is the second positional argument'},
           {'name': 'kwarg1':, 'type': (list, tuple), 'doc': 'this is a keyword argument', 'default': list()},
           returns='foo object', rtype='Foo')
   def foo(self, **kwargs):
       arg1, arg2, kwarg1 = getargs('arg1', 'arg2', 'kwarg1', **kwargs)
       ...


The ``'shape'`` parameter is a tuple that follows the same logic as the `shape parameter in the specification
language <https://schema-language.readthedocs.io/en/latest/description.html#shape>`_. It can take the form of a tuple
with integers or ``None`` in each dimension. ``None`` indicates that this dimension can take any value. For
instance, ``(3, None)`` means the data must be a 2D matrix with a length of 3 and any width. ``'shape'`` can also
take a value that is a tuple of tuples, in which case any one of those tuples can match the spec. For instance,
``"shape": ((3, 3), (4, 4, 4))`` would indicate that the shape of this data could either be 3x3 or 4x4x4.

The ``'type'`` argument can take a class or a tuple of classes. We also define special strings that are macros which
encompass a number of similar types, and can be used in place of a class, on its own, or within a tuple. ``'array_data'``
allows the data to be of type ``np.ndarray``, ``list``, ``tuple``, or ``h5py.Dataset``; and ``'scalar_data'`` allows
the data to be ``str``, ``int``, ``float``, ``bytes``, or ``bool``.

Registering classes
-------------------

When defining a class that represents a *neurodata_type* (i.e. anything that has a *neurodata_type_def*)
from your extension, you can tell PyNWB which *neurodata_type* it represents using the function
:py:func:`~pynwb.register_class`. This class can be called on its own, or used as a class decorator. The
first argument should be the *neurodata_type* and the second argument should be the *namespace* name.

The following example demonstrates how to register a class as the Python class representation of the
*neurodata_type* "MyContainer" from the *namespace* "my_ns".

.. code-block:: python

    from pynwb import register_class
    from pynwb.core import NWBContainer

    class MyContainer(NWBContainer):
        ...

    regitser_class('MyContainer', 'my_ns', MyContainer)


Alternatively, you can use :py:func:`~pynwb.register_class` as a decorator.

.. code-block:: python

    from pynwb import register_class
    from pynwb.core import NWBContainer

    @regitser_class('MyContainer', 'my_ns')
    class MyContainer(NWBContainer):
        ...

:py:func:`~pynwb.register_class` is used with :py:class:`~pynwb.core.NWBData` the same way it is used with
:py:class:`~pynwb.core.NWBContainer`.


Nwbfields
---------

When creating a new neurodata type, you need to define the new properties on your class, which is done by defining
them in the ``__nwbfields__`` class property. This class property should be a tuple of strings that name the new
properties. Adding a property using this functionality will create a property than can be set *only once*. Any
new properties of the class should be defined here.

For example, the following class definition will create the ``MyContainer`` class that has the properties ``foo``
and ``bar``.

.. code-block:: python

    from pynwb import register_class
    from pynwb.core import NWBContainer


    class MyContainer(NWBContainer):

        __nwbfields__ = ('foo', 'bar')

        ...


NWBContainer
-------------

:py:class:`~pynwb.core.NWBContainer` should be used to represent groups with a *neurodata_type_def*. This section
will discuss the available :py:class:`~pynwb.core.NWBContainer` subclasses for representing common group specifications.

NWBDataInterface
^^^^^^^^^^^^^^^^

The NWB schema uses the neurodata type ``NWBDataInterface`` for specifying containers that contain data that is not
considered metadata. For example, ``NWBDataInterface`` is a parent neurodata type to ``ElectricalSeries`` data,
but not a parent to ``ElectrodeGroup``.

There are no requirements for using :py:class:`~pynwb.core.NWBDataInterface` in addition to those inherited from
:py:class:`~pynwb.core.NWBContainer`.

MultiContainerInterface
^^^^^^^^^^^^^^^^^^^^^^^^

Throughout the NWB schema, there are multiple ``NWBDataInterface`` specifications that include one or more or zero
or more of a certain neurodata type. For example, the ``LFP`` neurodata type contains one or more ``ElectricalSeries``.
If your extension follows this pattern, you can use :py:class:`~pynwb.core.MultiContainerInterface` for defining
the representative class.

:py:class:`~pynwb.core.MultiContainerInterface` provides a way of automatically generating setters, getters, and
properties for your class. These methods are autogenerated based on a configuration provided using the class property
``__clsconf__``.  ``__clsconf__`` should be a dict or a list of dicts. A single dict should be used if your
specification contains a single neurodata type. A list of dicts should be used if your specification contains
multiple neurodata types that will exist as one or more or zero or more. The contents of the dict are described
in the following table.

===========  =========================================================== ================
  Key                     Attribute                                         Required?
===========  =========================================================== ================
``type``      the type of the Container                                    Yes
``attr``      the property name that holds the Containers                  Yes
``add``       the name of the method for adding a Container                Yes
``create``    the name of the method for creating a Container              No
``get``       the name of the method for getting a Container by name       Yes
===========  =========================================================== ================


The ``type`` key provides a way for the setters to check for type. The property under the name given by the.
``attr`` key will be a :py:class:`~pynwb.core.LabelledDict`. If your class uses a single dict,
a ``__getitem__`` method will be autogenerated for indexing into this :py:class:`~pynwb.core.LabelledDict`.
Finally, a constructor will also be autogenerated if you do not provide one in the  class definition.

The following code block demonstrates using :py:class:`~pynwb.core.MultiContainerInterface` to build a class
that represents the neurodata type "MyDataInterface" from the namespace "my_ns". It contains one or more containers
with neurodata type "MyContainer".

.. code-block:: python

    from pynwb import register_class
    from pynwb.core import MultiContainerInterface


    @register_class("MyDataInterface", "my_ns")
    class MyDataInterface(MultiContainerInterface):

        __clsconf__ = {
            'type': MyContainer,
            'attr': 'containers',
            'add': 'add_container',
            'create': 'create_container',
            'get': 'get_container',
        }
        ...


This class will have the methods ``add_container``, ``create_container``,  and ``get_container``. It will also have
the property ``containers``. The ``add_container`` method will check to make sure that either an object of type
``MyContainer`` or a list/dict/tuple of objects of type ``MyContainer`` is passed in. ``create_container`` will
accept the exact same arguments that the ``MyContainer`` class constructor accepts.

NWBData
--------

:py:class:`~pynwb.core.NWBData` should be used to represent datasets with a *neurodata_type_def*. This section
will discuss the available :py:class:`~pynwb.core.NWBData` subclasses for representing common dataset specifications.

NWBTable
^^^^^^^^^

If your specification extension contains a table definition i.e. a dataset with a compound data type, you should use
the :py:class:`~pynwb.core.NWBTable` class to represent this specification. Since :py:class:`~pynwb.core.NWBTable`
subclasses :py:class:`~pynwb.core.NWBData`, you can still use ``__nwbfields__``. In addition, you can use the
``__columns__`` class property to specify the columns of the table. ``__columns__`` should be a list or a tuple of
:py:func:`~hdmf.utils.docval`-like dictionaries.

The following example demonstrates how to define a table with the columns ``foo`` and ``bar`` that are of type
str and int, respectively. We also register the class as the representation of the *neurodata_type* "MyTable"
from the *namespace* "my_ns".

.. code-block:: python

    from pynwb import register_class
    from pynwb.core import NWBTable


    @register_class('MyTable', 'my_ns')
    class MyTable(NWBTable):

        __columns__ = [
            {'name': 'foo', 'type': str, 'doc': 'the foo column'},
            {'name': 'bar', 'type': int, 'doc': 'the bar column'},
        ]

        ...

NWBTableRegion
^^^^^^^^^^^^^^

:py:class:`~pynwb.core.NWBTableRegion` should be used to represent datasets that store a region reference.
When subclassing this class, make sure you provide a way to pass in the required
arguments for the :py:class:`~pynwb.core.NWBTableRegion` constructor--the *name* of the dataset, the *table* that the region
applies to, and the *region* itself.


ObjectMapper: Customizing the mapping between NWBContainer and the Spec
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If your :py:class:`~pynwb.core.NWBContainer` extension requires custom mapping of the
:py:class:`~pynwb.core.NWBContainer`
class for reading and writing, you will need to implement and register a custom
:py:class:`~hdmf.build.objectmapper.ObjectMapper`.

:py:class:`~hdmf.build.objectmapper.ObjectMapper` extensions are registered with the decorator
:py:func:`~pynwb.register_map`.

.. code-block:: python

    from pynwb import register_map
    from hdmf.build import ObjectMapper

    @register_map(MyExtensionContainer)
    class MyExtensionMapper(ObjectMapper)
        ...

:py:func:`~pynwb.register_map` can also be used as a function.

.. code-block:: python

    from pynwb import register_map
    from hdmf.build import ObjectMapper

    class MyExtensionMapper(ObjectMapper)
        ...

    register_map(MyExtensionContainer, MyExtensionMapper)

.. tip::

    ObjectMappers allow you to customize how objects in the spec are mapped to attributes of your NWBContainer in
    Python. This is useful, e.g., in cases where you want to customize the default mapping. For example in
    ``TimeSeries``, the attribute ``unit``, which is defined on the dataset ``data`` (i.e., ``data.unit``), would
    by default be mapped to the attribute ``data__unit`` on :py:class:`~pynwb.base.TimeSeries`. The ObjectMapper
    :py:class:`~pynwb.io.base.TimeSeriesMap` then changes this mapping to map ``data.unit`` to the attribute ``unit``
    on :py:class:`~pynwb.base.TimeSeries` . ObjectMappers also allow you to customize how constructor arguments
    for your ``NWBContainer`` are constructed. For example, in ``TimeSeries`` instead of explicit ``timestamps`` we
    may only have a ``starting_time`` and ``rate``. In the ObjectMapper, we could then construct ``timestamps``
    from this data on data load to always have ``timestamps`` available for the user.
    For an overview of the concepts of containers, spec, builders, and object mappers in PyNWB, see also
    :ref:`software-architecture`.
