Building API classes
====================

After you have written an extension, you will need a Pythonic way to interact with the data model. To do this,
you will need to write some classes that represent the data you defined in your specificiation extensions.
The :py:mod:`pynwb.core` module has various tools to make it easier to write classes that behave like
the rest of the PyNWB API.

The :py:mod:`pynwb.core` defines two base classes that represent the primitive structures supported by
the schema. :py:class:`~pynwb.core.NWBData` represents datasets and :py:class:`~pynwb.core.NWBContainer`
represents groups. Additionally, :py:mod:`pynwb.core` offers subclasses of these two classes for
writing classes that come with more functionality.

``register_class``
------------------

When defining a class that represents a *neurodata_type* (i.e. anything that has a *neurodata_type_def*)
from your extension, you can tell PyNWB which *neurodata_type* it represents using the function
:py:func:`~pynwb.register_class`. This class can be called on its own, or used as a class decorator. The
first argument should be the *neurodata_type* and the second argument should be the *namespace* name.

The following example demonstrates how to register a class as the Python class reprsentation of the
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


``__nwbfields__``
-----------------

When subclassing :py:class:`~pynwb.core.NWBData` or :py:class:`~pynwb.core.NWBContainer`, you might want to
define some properties on your class. This can be done using the ``__nwbfields__`` class property. This
class property should be a tuple of strings that name the properties. Adding a property using this functionality
will create a property than can be set *only once*.

For example, the following class definition will create the ``MyContainer`` class that has the properties ``foo``
and ``bar``.

.. code-block:: python

    from pynwb import register_class
    from pynwb.core import NWBContainer


    class MyContainer(NWBContainer):

        __nwbfields__ = ('foo', 'bar')

        ...


``NWBData``
-----------

:py:class:`~pynwb.core.NWBData` should be used to represent datasets with a *neurodata_type_def*. This section
 will discuss the available :py:class:`~pynwb.core.NWBData` subclasses for representing common dataset specifications.

``NWBTable``
^^^^^^^^^^^^

If your specification extension contains a table definition i.e. a dataset with a compound data type, you should use
the :py:class:`~pynwb.core.NWBTable` class to represent this specification. Since :py:class:`~pynwb.core.NWBTable`
subclasses :py:class:`~pynwb.core.NWBData` you can still use ``__nwbfields__``. In addition, you can use the
``__columns__`` class property to specify the columns of the table. ``__columns__`` should be a list or a tuple of
:py:func:`~hdmf.utils.docval`-like dictionaries.

The following example demonstrates how to define a table with the columns ``foo`` and ``bar`` that are of type
str and int, respectively. We also register the class as the reppresentation of the *neurodata_type* "MyTable"
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

``NWBTableRegion``
^^^^^^^^^^^^^^^^^^

:py:class:`~pynwb.core.NWBTableRegion` should be used to represent datasets that store a region reference. The constructor
for :py:class:`~pynwb.core.NWBTableRegion`. When subclassing this class, make sure you provide a way to pass in the required
arguments for the :py:class:`~pynwb.core.NWBTableRegion` constructor--the *name* of the dataset, the *table* that the region
applies to, and the *region* itself.


``NWBContainer``
----------------

:py:class:`~pynwb.core.NWBContainer`
should be used to represent groups with a *neurodata_type_def*. This section
will discuss the available :py:class:`~pynwb.core.NWBContainer` subclasses for representing common group specifications.

``NWBDataInterface``
^^^^^^^^^^^^^^^^^^^^

The NWB schema users the neurodata type *NWBDataInterface* for specifying containers that contain data that is not
considered metadata. For example, *NWBDataInterface* is a parent neurodata type to *ElectricalSeries* data,
but not a parent to *ElectrodeGroup*.

There are no requirements for using :py:class:`~pynwb.core.NWBDataInterface` in addition to those inherited from
:py:class:`~pynwb.core.NWBContainer`.

``MultiContainerInterface``
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Throughout the NWB schema, there are multiple *NWBDataInterface* specifications that include one or more or zero
or more of a certain neurodata type. For example, the *LFP* neurodata type contains one or more *ElectricalSeries*.
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
