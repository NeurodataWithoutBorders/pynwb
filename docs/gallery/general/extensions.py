'''
Extensions
=========================

The NWB-N format was designed to be easily extendable. Here we will demonstrate how to extend NWB using the
PyNWB API.
'''

####################
# Defining extensions
# -----------------------------------------------------
#
# Extensions should be defined separately from the code that uses the extensions. This design decision is
# based on the assumption that extension will be written once, and read or used multiple times. Here, we
# provide an example of how to create an extension for subsequent use.
# (For more information on the available tools for creating extensions, see :ref:`extending-nwb`).
#
#
# The following block of code demonstrates how to create a new namespace, and then add a new `neurodata_type`
# to this namespace. Finally,
# it calls :py:meth:`~form.spec.write.NamespaceBuilder.export` to save the extensions to disk for downstream use.

from pynwb.spec import NWBNamespaceBuilder, NWBGroupSpec, NWBAttributeSpec

ns_path = "mylab.namespace.yaml"
ext_source = "mylab.extensions.yaml"

ns_builder = NWBNamespaceBuilder('Extension for use in my Lab', "mylab")
ext = NWBGroupSpec('A custom ElectricalSeries for my lab',
                   attributes=[NWBAttributeSpec('trode_id', 'int', 'the tetrode id')],
                   neurodata_type_inc='ElectricalSeries',
                   neurodata_type_def='TetrodeSeries')

ns_builder.add_spec(ext_source, ext)
ns_builder.export(ns_path)

####################
# Running this block will produce two YAML files.
#
# The first file contains the specification of the namespace.
#
# .. code-block:: yaml
#
#     # mylab.namespace.yaml
#     namespaces:
#     - doc: Extension for use in my Lab
#       name: mylab
#       schema:
#       - namespace: core
#       - source: fake_extension.yaml
#
# The second file contains the details on newly defined types.
#
# .. code-block:: yaml
#
#     # mylab.extensions.yaml
#     groups:
#     - attributes:
#       - doc: the tetrode id
#         dtype: int
#         name: trode_id
#       doc: A custom ElectricalSeries for my lab
#       neurodata_type_def: TetrodeSeries
#       neurodata_type_inc: ElectricalSeries
#
# .. tip::
#
#     Detailed documentation of all components and `neurodata_types` that are part of the core schema of NWB:N are
#     available in the schema docs at `http://nwb-schema.readthedocs.io <http://nwb-schema.readthedocs.io>`_ .
#     Before creating a new type from scratch, please have a look at the schema docs to see if using or extending an
#     existing type may solve your problem. Also, the schema docs are helpful when extending an existing type to
#     better understand the design and structure of the neurodata_type you are using.


####################
# Using extensions
# -----------------------------------------------------
#
# After an extension has been created, it can be used by downstream codes for reading and writing data.
# There are two main mechanisms for reading and writing extension data with PyNWB.
# The first involves defining new :py:class:`~pynwb.core.NWBContainer` classes that are then mapped
# to the neurodata types in the extension.


from pynwb import register_class, load_namespaces
from pynwb.ecephys import ElectricalSeries

ns_path = "mylab.namespace.yaml"
load_namespaces(ns_path)


@register_class('TetrodeSeries', 'mylab')
class TetrodeSeries(ElectricalSeries):
    __nwbfields__ = ('tetrode_id',)

    def __init__(self, *args, **kwargs):
        pass

####################
# .. note::
#
#     Although it is not used here, it is encouraged to use the :py:func:`~form.utils.docval`
#     decorator for documenting constructors, methods, and functions.
#
# When extending :py:class:`~pynwb.core.NWBContainer` or :py:class:`~pynwb.core.NWBContainer`
# subclasses, you should defining the class field ``__nwbfields__``. This will
# tell PyNWB the properties of the :py:class:`~pynwb.core.NWBContainer` extension.
#
# If you do not want to write additional code to read your extensions, PyNWB is able to dynamically
# create an :py:class:`~pynwb.core.NWBContainer` subclass for use within the PyNWB API.
# Dynamically created classes can be inspected using the built-in :py:func:`.help` or the :py:mod:`inspect` module.


from pynwb import get_class, load_namespaces

ns_path = "mylab.namespace.yaml"
load_namespaces(ns_path)

AutoTetrodeSeries = get_class('TetrodeSeries', 'mylab')

####################
# .. note::
#
#     When defining your own :py:class:`~pynwb.core.NWBContainer`, the subclass name does not need to be the same
#     as the extension type name. However, it is encouraged to keep class and extension names the same for the
#     purposes of readibility.


####################
# Example: Cortical Surface Mesh
# -----------------------------------------------------
#
# Here we show how to create extensions by example by creating a data class for a
# cortical surface mesh. This data type is particularly important for ECoG data, we need to know where each electrode is
# with respect to the gyri and sucli. Surface mesh objects contain two types of data:
# 1. `vertices`, which is an (n,3) matrix of floats that represents points in 3D space
# 2. `faces`, which is an (n,3) matrix of uints that represents indices of the `vertices` matrix. Each triplet of points
# defines a triangular face, and the mesh is comprised of a collection of triangular faces.
#
# First, we set up our extension. I am going to use the name `ecog`

from pynwb.spec import NWBDatasetSpec, NWBNamespaceBuilder, NWBGroupSpec

name = 'ecog'
ns_path = name + ".namespace.yaml"
ext_source = name + ".extensions.yaml"

# Now we define the data structures. We use `NWBDataInterface` as the base type,
# which is the lowest type you are likely to use as a base. The name of the
# class is `CorticalSurface`, and it requires two matrices, `vertices` and
# `faces`.

surface = NWBGroupSpec(doc='brain cortical surface',
                       datasets=[
                           NWBDatasetSpec(doc='faces for surface, indexes vertices', shape=(None, 3),
                                          name='faces', dtype='uint', dims=('face_number', 'vertex_index')),
                           NWBDatasetSpec(doc='vertices for surface, points in 3D space', shape=(None, 3),
                                          name='vertices', dtype='float', dims=('vertex_number', 'xyz'))],
                       neurodata_type_def='CorticalSurface',
                       neurodata_type_inc='NWBDataInterface')

# Now we set up the builder and add this object

ns_builder = NWBNamespaceBuilder(name + ' extensions', name)
ns_builder.add_spec(ext_source, surface)
ns_builder.export(ns_path)

# The above should generate 2 YAML files. `ecog.extensions.yaml`,
# defines the newly defined types
#
# .. code-block:: yaml
#
#     # ecog.namespace.yaml
#       groups:
#       - datasets:
#       - dims:
#           - face_number
#           - vertex_index
#           doc: faces for surface, indexes vertices
#           dtype: uint
#           name: faces
#           shape:
#           - null
#           - 3
#       - dims:
#           - vertex_number
#           - xyz
#           doc: vertices for surface, points in 3D space
#           dtype: float
#           name: vertices
#           shape:
#           - null
#           - 3
#       doc: brain cortical surface
#       neurodata_type_def: CorticalSurface
#       neurodata_type_inc: NWBDataInterface
#
# Finally, we should test the new types to make sure they run as expected

from pynwb import load_namespaces, get_class, NWBHDF5IO, NWBFile
from datetime import datetime

load_namespaces('ecog.namespace.yaml')
CorticalSurface = get_class('CorticalSurface', 'ecog')

cortical_surface = CorticalSurface(vertices=[[0.0, 1.0, 1.0],
                                             [1.0, 1.0, 2.0],
                                             [2.0, 2.0, 1.0],
                                             [2.0, 1.0, 1.0],
                                             [1.0, 2.0, 1.0]],
                                   faces=[[0, 1, 2],
                                          [1, 2, 3]],
                                   name='cortex',
                                   source='source')

nwbfile = NWBFile('name', 'my first synthetic recording',
                  'EXAMPLE_ID', datetime.now())

cortex_module = nwbfile.create_processing_module(name='cortex',
                                                 description='description',
                                                 source='source')
cortex_module.add_container(cortical_surface)


with NWBHDF5IO('test_cortical_surface.nwb', 'w') as io:
    io.write(nwbfile)






