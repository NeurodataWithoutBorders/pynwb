'''
.. _tutorial-extending-nwb:

Extensions
=========================

The NWB:N format was designed to be easily extendable. Here we will demonstrate how to extend NWB using the
PyNWB API.

.. note::

    A more in-depth discussion of the components and steps for creating and using extensions is
    available as part of the docs at :ref:`extending-nwb`.

'''

####################
# .. _defining_extension:
#
# Defining extensions
# -----------------------------------------------------
#
# Extensions should be defined separately from the code that uses the extensions. This design decision is
# based on the assumption that the extension will be written once, and read or used multiple times. Here, we
# provide an example of how to create an extension for subsequent use.
# (For more information on the available tools for creating extensions, see :ref:`extending-nwb`).
#
#
# The following block of code demonstrates how to create a new namespace, and then add a new `neurodata_type`
# to this namespace. Finally,
# it calls :py:meth:`~hdmf.spec.write.NamespaceBuilder.export` to save the extensions to disk for downstream use.

from pynwb.spec import NWBNamespaceBuilder, NWBGroupSpec, NWBAttributeSpec

ns_path = "mylab.namespace.yaml"
ext_source = "mylab.extensions.yaml"

ns_builder = NWBNamespaceBuilder('Extension for use in my Lab', "mylab")

ns_builder.include_type('ElectricalSeries', namespace='core')

ext = NWBGroupSpec('A custom ElectricalSeries for my lab',
                   attributes=[NWBAttributeSpec('trode_id', 'the tetrode id', 'int')],
                   neurodata_type_inc='ElectricalSeries',
                   neurodata_type_def='TetrodeSeries')

ns_builder.add_spec(ext_source, ext)
ns_builder.export(ns_path)

####################
# Running this block will produce two YAML files.
#
# The first file, mylab.namespace.yaml, contains the specification of the namespace.
#
# .. code-block:: yaml
#
#     namespaces:
#     - doc: Extension for use in my Lab
#       name: mylab
#       schema:
#       - namespace: core
#         neurodata_type:
#         - ElectricalSeries
#       - source: mylab.extensions.yaml
#
# The second file, mylab.extensions.yaml, contains the details on newly defined types.
#
# .. code-block:: yaml
#
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
# .. _using_extension:
#
# Using extensions
# -----------------------------------------------------
#
# After an extension has been created, it can be used by downstream codes for reading and writing data.
# There are two main mechanisms for reading and writing extension data with PyNWB.
# The first involves defining new :py:class:`~pynwb.core.NWBContainer` classes that are then mapped
# to the neurodata types in the extension.


from pynwb import register_class, load_namespaces
from pynwb.ecephys import ElectricalSeries
from hdmf.utils import docval, call_docval_func, getargs, get_docval

ns_path = "mylab.namespace.yaml"
load_namespaces(ns_path)


@register_class('TetrodeSeries', 'mylab')
class TetrodeSeries(ElectricalSeries):

    __nwbfields__ = ('trode_id',)

    @docval(*get_docval(ElectricalSeries.__init__) + (
        {'name': 'trode_id', 'type': int, 'doc': 'the tetrode id'},))
    def __init__(self, **kwargs):
        call_docval_func(super(TetrodeSeries, self).__init__, kwargs)
        self.trode_id = getargs('trode_id', kwargs)


####################
# .. note::
#
#     See the API docs for more information about :py:func:`~hdmf.utils.docval`
#     :py:func:`~hdmf.utils.call_docval_func`, :py:func:`~hdmf.utils.getargs`
#     and :py:func:`~hdmf.utils.get_docval`
#
# When extending :py:class:`~pynwb.core.NWBContainer` or :py:class:`~pynwb.core.NWBContainer`
# subclasses, you should define the class field ``__nwbfields__``. This will
# tell PyNWB the properties of the :py:class:`~pynwb.core.NWBContainer` extension.
#
# If you do not want to write additional code to read your extensions, PyNWB is able to dynamically
# create an :py:class:`~pynwb.core.NWBContainer` subclass for use within the PyNWB API.
# Dynamically created classes can be inspected using the built-in :py:mod:`inspect` module.


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
# .. _caching_extension:
#
# Caching extensions to file
# -----------------------------------------------------
#
# By default, extensions are cached to file so that your NWB file will carry the extensions needed to read the file
# with it.
#
# To demonstrate this, first we will make some fake data using our extensions.

from datetime import datetime
from dateutil.tz import tzlocal
from pynwb import NWBFile

start_time = datetime(2017, 4, 3, 11, tzinfo=tzlocal())
create_date = datetime(2017, 4, 15, 12, tzinfo=tzlocal())

nwbfile = NWBFile('demonstrate caching', 'NWB456', start_time,
                  file_create_date=create_date)

device = nwbfile.create_device(name='trodes_rig123')

electrode_name = 'tetrode1'
description = "an example tetrode"
location = "somewhere in the hippocampus"

electrode_group = nwbfile.create_electrode_group(electrode_name,
                                                 description=description,
                                                 location=location,
                                                 device=device)
for idx in [1, 2, 3, 4]:
    nwbfile.add_electrode(idx,
                          x=1.0, y=2.0, z=3.0,
                          imp=float(-idx),
                          location='CA1', filtering='none',
                          group=electrode_group)
electrode_table_region = nwbfile.create_electrode_table_region([0, 2], 'the first and third electrodes')

import numpy as np

rate = 10.0
np.random.seed(1234)
data_len = 1000
data = np.random.rand(data_len * 2).reshape((data_len, 2))
timestamps = np.arange(data_len) / rate

ts = TetrodeSeries('test_ephys_data',
                   data,
                   electrode_table_region,
                   timestamps=timestamps,
                   trode_id=1,
                   # Alternatively, could specify starting_time and rate as follows
                   # starting_time=ephys_timestamps[0],
                   # rate=rate,
                   resolution=0.001,
                   comments="This data was randomly generated with numpy, using 1234 as the seed",
                   description="Random numbers generated with numpy.random.rand")
nwbfile.add_acquisition(ts)

####################
# .. note::
#
#     For more information on writing :py:class:`~pynwb.ecephys.ElectricalSeries`,
#     see :ref:`ecephys_tutorial`.
#
# Now that we have some data, lets write our file. You can choose not to cache the spec by setting
# cache_spec=False in :py:meth:`~hdmf.backends.hdf5.h5tools.HDF5IO.write`

from pynwb import NWBHDF5IO

io = NWBHDF5IO('cache_spec_example.nwb', mode='w')
io.write(nwbfile)
io.close()

####################
# .. note::
#
#     For more information on writing NWB files, see :ref:`basic_writing`.

####################
# By default, PyNWB does not use the namespaces cached in a file--you must
# explicitly specify this. This behavior is enabled by the *load_namespaces*
# argument to the :py:class:`~pynwb.NWBHDF5IO` constructor.

io = NWBHDF5IO('cache_spec_example.nwb', mode='r', load_namespaces=True)
nwbfile = io.read()

####################
# .. _MultiContainerInterface:
#
# Creating and using a custom MultiContainerInterface
# -----------------------------------------------------
# It is sometimes the case that we need a group to hold zero-or-more or
# one-or-more of the same object. Here we show how to create an extension that
# defines a group (`PotatoSack`) that holds multiple objects (`Pototo` es) and
# then how to use the new data types. First, we use `pynwb` to define the new
# data types.

from pynwb.spec import NWBNamespaceBuilder, NWBGroupSpec, NWBAttributeSpec

name = 'test_multicontainerinterface'
ns_path = name + ".namespace.yaml"
ext_source = name + ".extensions.yaml"

ns_builder = NWBNamespaceBuilder(name + ' extensions', name)
ns_builder.include_type('NWBDataInterface', namespace='core')

potato = NWBGroupSpec(neurodata_type_def='Potato',
                      neurodata_type_inc='NWBDataInterface',
                      doc='A potato', quantity='*',
                      attributes=[
                          NWBAttributeSpec(name='weight',
                                           doc='weight of potato',
                                           dtype='float',
                                           required=True),
                          NWBAttributeSpec(name='age',
                                           doc='age of potato',
                                           dtype='float',
                                           required=False))
                      ])

potato_sack = NWBGroupSpec(neurodata_type_def='PotatoSack',
                           neurodata_type_inc='NWBDataInterface',
                           name='potato_sack',
                           doc='A sack of potatoes', quantity='?',
                           groups=[potato])

ns_builder.add_spec(ext_source, potato_sack)
ns_builder.export(ns_path)

####################
# Then create Container classes registered to the new data types (this is
# generally done in a different file)

from pynwb import register_class, load_namespaces
from pynwb.file import MultiContainerInterface, NWBContainer

load_namespaces(ns_path)


@register_class('Potato', name)
class Potato(NWBContainer):
    __nwbfields__ = ('name', 'weight', 'age')

    @docval({'name': 'name', 'type': str, 'doc': 'who names a potato?'},
            {'name': 'weight', 'type': float, 'doc': 'weight of potato in grams'},
            {'name': 'age', 'type': float, 'doc': 'age of potato in days'})
    def __init__(self, **kwargs):
        super(Potato, self).__init__(name=kwargs['name'])
        self.weight = kwargs['weight']
        self.age = kwargs['age']


@register_class('PotatoSack', name)
class PotatoSack(MultiContainerInterface):

    __clsconf__ = {
        'attr': 'potatoes',
        'type': Potato,
        'add': 'add_potato',
        'get': 'get_potato',
        'create': 'create_potato',
    }


####################
# Then use the objects (again, this would often be done in a different file).

from pynwb import NWBHDF5IO, NWBFile
from datetime import datetime
from dateutil.tz import tzlocal

# You can add potatoes to a potato sack in different ways
potato_sack = PotatoSack(potatoes=Potato(name='potato1', age=2.3, weight=3.0))
potato_sack.add_potato(Potato('potato2', 3.0, 4.0))
potato_sack.create_potato('big_potato', 10.0, 20.0)

nwbfile = NWBFile("a file with metadata", "NB123A", datetime(2018, 6, 1, tzinfo=tzlocal()))

pmod = nwbfile.create_processing_module('module_name', 'desc')
pmod.add_container(potato_sack)


with NWBHDF5IO('test_multicontainerinterface.nwb', 'w') as io:
    io.write(nwbfile)

####################
# This is how you read the NWB file (again, this would often be done in a
# different file).

load_namespaces(ns_path)
# from xxx import PotatoSack, Potato
io = NWBHDF5IO('test_multicontainerinterface.nwb', 'r')
nwb = io.read()
print(nwb.get_processing_module()['potato_sack'].get_potato('big_potato').weight)
# note: you can call get_processing_module() with or without the module name as
# an argument. however, if there is more than one module, the name is required.
# here, there is more than one potato, so the name of the potato is required as
# an argument to get get_potato

io.close()
