from .spec import BaseStorageSpec
from ..utils import docval, getargs, popargs, get_docval

class SpecCatalog(object):

    def __init__(self):
        '''
        Create a new catalog for storing specifications

        ** Private Instance Variables **

        :ivar __specs: Dict with the specification of each registered type
        :ivar __parent_types: Dict with parent types for each registered type
        :ivar __spec_source_files: Dict with the path to the source files (if available) for each registered type

        '''
        self.__specs = dict()
        self.__parent_types = dict()
        self.__spec_source_files = dict()

    @docval({'name': 'spec', 'type': BaseStorageSpec, 'doc': 'a Spec object'},
            {'name': 'source_file', 'type': str, 'doc': 'path to the source file from which the spec was loaded', 'default': None})
    def register_spec(self, **kwargs):
        '''
        Associate a specified object type with an HDF5 specification
        '''
        spec, source_file = getargs('spec', 'source_file', kwargs)
        ndt = spec.data_type_inc
        ndt_def = spec.data_type_def
        if ndt_def is None:
            raise ValueError('cannot register spec that has no data_type_def')
        if ndt_def != ndt:
            self.__parent_types[ndt_def] = ndt
        type_name = ndt_def if ndt_def is not None else ndt
        if type_name in self.__specs:
            raise ValueError("'%s' - cannot overwrite existing specification" % type_name)
        self.__specs[type_name] = spec
        self.__spec_source_files[type_name] = source_file

    @docval({'name': 'data_type', 'type': str, 'doc': 'the data_type to get the Spec for'},
            returns="the specification for writing the given object type to HDF5 ", rtype='Spec')
    def get_spec(self, **kwargs):
        '''
        Get the Spec object for the given type
        '''
        data_type = getargs('data_type', kwargs)
        return self.__specs.get(data_type, None)

    def get_registered_types(self):
        '''
        Return all registered specifications
        '''
        return tuple(self.__specs.keys())

    @docval({'name': 'data_type', 'type': str, 'doc': 'the data_type of the spec to get the source file for'},
            returns="the path to source specification file from which the spec was orignially loaded or None ",
            rtype='str')
    def get_spec_source_file(self, **kwargs):
        '''
        Return the path to the source file from which the spec for the given
        type was loaded from. None is returned if no file path is available
        for the spec. Note: The spec in the file may not be identical to the
        object in case teh spec is modified after load.
        '''
        data_type = getargs('data_type', kwargs)
        return self.__spec_source_files.get(data_type, None)

    @docval({'name': 'spec', 'type': BaseStorageSpec, 'doc': 'the Spec object to register'},
            {'name': 'source_file', 'type': str, 'doc': 'path to the source file from which the spec was loaded', 'default': None})
    def auto_register(self, **kwargs):
        '''
        Register this specification and all sub-specification using data_type as object type name
        '''
        spec, source_file = getargs('spec', 'source_file', kwargs)
        ndt = spec.data_type_def
        if ndt is not None:
            self.register_spec(spec, source_file)
        for dataset_spec in spec.datasets:
            dset_ndt = dataset_spec.data_type_def
            if dset_ndt is not None:
                self.register_spec(dataset_spec, source_file)
        for group_spec in spec.groups:
            self.auto_register(group_spec, source_file)

    def __copy__(self):
        ret = SpecCatalog()
        ret.__specs = copy.copy(spec)
        return ret

    def __deepcopy__(self):
        ret = SpecCatalog()
        ret.__specs = copy.deepcopy(spec)
        return ret

