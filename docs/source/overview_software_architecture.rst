.. _software-architecture:

Software Architecture
=====================

The main goal of PyNWB is to enable users and developers to efficiently interact with the NWB data format,
format files, and specifications. The following figures provide an overview of the high-level architecture of
PyNWB and functionality of the various components.

.. _fig-software-architecture:

.. figure:: figures/software_architecture.*
   :width: 100%
   :alt: PyNWB Software Architecture

   Overview of the high-level software architecture of PyNWB (click to enlarge).


.. _fig-software-architecture-purpose:

.. figure:: figures/software_architecture_design_choices.*
   :width: 100%
   :alt: PyNWB Software Architecture Functions

   We choose a modular design for PyNWB to enable flexibility and separate the
   various aspects of the NWB:N ecosystem (click to enlarge).

.. raw:: latex

    \clearpage \newpage


Main Concepts
-------------


.. _fig-software-architecture-concepts:

.. figure:: figures/software_architecture_concepts.*
   :width: 100%
   :alt: PyNWB Software Architecture Concepts

   Overview of the main concepts/classes in PyNWB and their location in the overall software architecture (click to enlarge).

Container
^^^^^^^^^

* In memory objects
* Interface for (most) applications
* Like a table row
* PyNWB has many of these -- one for each neurodata_type in the NWB schema. PyNWB organizes the containers
  into a set of modules based on their primary application (e.g., ophys for optophysiology):

   * :py:class:`pynwb.base`, :py:class:`pynwb.file`
   * :py:class:`pynwb.ecephys`
   * :py:class:`pynwb.ophys`
   * :py:class:`pynwb.icephys`
   * :py:class:`pynwb.ogen`
   * :py:class:`pynwb.behavior`

Builder
^^^^^^^

* Intermediary objects for I/O
* Interface for I/O
* Backend readers and writers must return and accept these
* There are different kinds of builders for different base types:

   * :py:class:`~hdmf.build.builders.GroupBuilder` - represents a collection of objects
   * :py:class:`~hdmf.build.builders.DatasetBuilder` - represents data
   * :py:class:`~hdmf.build.builders.LinkBuilder` - represents soft-links
   * :py:class:`~hdmf.build.builders.RegionBuilder` - represents a slice into data (Subclass of :py:class:`~hdmf.build.builders.DatasetBuilder`)

* **Main Module:** :py:mod:`hdmf.build.builders`

Spec
^^^^

* Interact with format specifications
* Data structures to specify data types and what said types consist of
* Python representation for YAML specifications
* Interface for writing extensions or custom specification
* There are several main specification classes:

   * :py:class:`~pynwb.spec.NWBAttributeSpec` - specification for metadata
   * :py:class:`~pynwb.spec.NWBGroupSpec` - specification for a collection of
     objects (i.e. subgroups, datasets, link)
   * :py:class:`~pynwb.spec.NWBDatasetSpec` - specification for dataset (like
     and n-dimensional array). Specifies data type, dimensions, etc.
   * :py:class:`~pynwb.spec.NWBLinkSpec` - specification for link (like a POSIX
     soft link)
   * :py:class:`~hdmf.spec.spec.RefSpec` - specification for references
     (References are like links, but stored as data)
   * :py:class:`~pynwb.spec.NWBDtypeSpec` - specification for compound data
     types. Used to build complex data type specification, e.g., to define
     tables (used only in :py:class:`~hdmf.spec.spec.DatasetSpec` and
     correspondingly :py:class:`~pynwb.spec.NWBDatasetSpec`)

* **Main Modules:**

   * :py:mod:`hdmf.spec` -- General specification classes.
   * :py:mod:`pynwb.spec` -- NWB specification classes. (Most of these are
     specializations of the classes from :py:mod:`hdmf.spec`)

.. note::

   A ``data_type`` (or more specifically a ``neurodata_type`` in the context of
   NWB) defines a reusable type in a format specification that can be
   referenced and used elsewhere in other specifications.  The specification of
   the NWB format is basically a collection of ``neurodata_types``, e.g.:
   ``NWBFile`` defines  a GroupSpec for the top-level group of an NWB format
   file  which includes ``TimeSeries``, ``ElectrodeGroup``, ``ImagingPlane``
   and many other ``neurodata_types`` .  When creating a specification, two
   main keys are used to include and define new ``neurodata_types``

   * ``neurodata_type_inc`` is used to include an existing type and
   * ``neurodata_type_def`` is used to define a new type

   I.e, if both keys are defined then we create a new type that uses/inherits
   an existing type as a base.

ObjectMapper
^^^^^^^^^^^^

* Maintains the mapping between `Container`_ attributes and `Spec`_ components
* Provides a way of converting between `Container`_ and `Builder`_
* ObjectMappers are constructed using a `Spec`_
* Ideally, one ObjectMapper for each data type
* Things an ObjectMapper should do:

   * Given a `Builder`_, return a Container representation
   * Given a `Container`_, return a Builder representation

* PyNWB has many of these -- one for each type in NWB schema
* **Main Module:** :py:mod:`hdmf.build.objectmapper`

   * NWB-specific ObjectMappers are locate in submodules of :py:class:`pynwb.io`

.. _fig-software-architecture-mainconcepts:

.. figure:: figures/software_architecture_mainconcepts.*
   :width: 100%
   :alt: PyNWB Software Architecture Main Concepts

   Relationship between `Container`_, `Builder`_, `ObjectMapper`_, and `Spec`_


Additional Concepts
-------------------

Namespace, NamespaceCatalog, NamespaceBuilder
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* **Namespace**

   * A namespace for specifications
   * Necessary for making extensions
   * Contains basic info about who created extensions
   * Core NWB:N schema has namespace “core”
   * Get from :py:class:`pynwb.spec.NWBNamespace`

      * extension of generic Namespace class that will include core

* :py:class:`~hdmf.spec.namespace.NamespaceCatalog` -- A class for managing namespaces
* :py:class:`~hdmf.spec.write.NamespaceBuilder` -- A utility for building extensions


TypeMap
^^^^^^^

* Map between data types, Container classes (i.e. a Python class object) and corresponding ObjectMapper classes
* Constructed from a NamespaceCatalog
* Things a TypeMap does:

   * Given an NWB data type, return the associated Container class
   * Given a Container class, return the associated ObjectMapper

* PyNWB has two of these classes:

   * the base class (i.e. :py:class:`~hdmf.build.manager.TypeMap`) - handles NWB 2.x
   * :py:class:`pynwb.legacy.map.TypeMapLegacy` - handles NWB 1.x

* PyNWB provides a “global” instance of TypeMap created at runtime
* TypeMaps can be merged, which is useful when combining extensions


BuildManager
^^^^^^^^^^^^

* Responsible for `memoizing <https://en.wikipedia.org/wiki/Memoization>`_ `Builder`_ and `Container`_
* Constructed from a `TypeMap`_
* PyNWB only has one of these: :py:class:`hdmf.build.manager.BuildManager`

.. _fig-software-architecture-buildmanager:

.. figure:: figures/software_architecture_buildmanager.*
   :width: 100%
   :alt: PyNWB Software Architecture BuildManager and TypeMap

   Overview of `BuildManager`_ (and `TypeMap`_) (click to enlarge).


HDMFIO
^^^^^^

* Abstract base class for I/O
* :py:class:`HDMFIO <hdmf.backends.io.HDMFIO>` has two key abstract methods:

   * :py:meth:`~hdmf.backends.io.HDMFIO.write_builder` – given a builder, write data to storage format
   * :py:meth:`~hdmf.backends.io.HDMFIO.read_builder` – given a handle to storage format, return builder representation
   * Others: :py:meth:`~hdmf.backends.io.HDMFIO.open` and :py:meth:`~hdmf.backends.io.HDMFIO.close`

* Constructed with a `BuildManager`_
* Extend this for creating a new I/O backend
* PyNWB has one extension of this:

   * :py:class:`~hdmf.backends.hdf5.h5tools.HDF5IO` - reading and writing HDF5
   * :py:class:`~pynwb.NWBHDF5IO` - wrapper that pulls in core NWB specification


.. _fig-software-architecture-formio:

.. figure:: figures/software_architecture_formio.*
   :width: 100%
   :alt: PyNWB Software Architecture FormIO

   Overview of `HDMFIO`_ (click to enlarge).
