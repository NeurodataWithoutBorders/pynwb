import h5py
from pynwb.validate import validate
from pynwb import NWBHDF5IO

path = 'tests/back_compat/2.1.0_nwbfile_with_extension.nwb'
io = NWBHDF5IO('tests/back_compat/2.1.0_nwbfile_with_extension.nwb')

print('Validating all with paths')
validate(paths=[path], namespace="core", verbose=True)

print('Validating core with io')
validate(io=io, namespace="core", verbose=True)

print('Validating core with paths')
validate(paths=[path], namespace="core", verbose=True)

print('Validating all with io')
validate(io=io, verbose=True, use_cached_namespaces=False)

#namespace_dependencies = NWBHDF5IO.get_namespaces(namespace_catalog=catalog, file=io._HDF5IO__file)
#io.get_namespaces(file=io._HDF5IO__file)
# manager = io.manager
# io.manager.namespace_catalog.get_namespace('name') then can get dependencies from that
# manager.namespace_catalog._NamespaceCatalog__namespaces

print('done')