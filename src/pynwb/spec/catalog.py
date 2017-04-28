from .spec import BaseStorageSpec
from pynwb.utils import docval, getargs, popargs, get_docval

class SpecCatalog(object):

    def __init__(self):
        '''
        Create a new catalog for storing specifications

        ** Private Instance Variables **

        :ivar __specs: Dict with the specification of each registered type
        :ivar __parent_types: Dict with parent types for each registered type
        :ivar __spec_source_files: Dict with the path to the source files (if available) for each registered type
        :ivar __hierarchy: Dict describing the hierarchy for each registered type.
                    NOTE: Always use SpecCatalog.get_hierarchy(...) to retrieve the hierarchy
                    as this dictionary is used like a cache, i.e., to avoid repeated calcuation
                    of the hierarchy but the contents are computed on first request by SpecCatalog.get_hierarchy(...)

        '''
        self.__specs = dict()
        self.__parent_types = dict()
        self.__hierarchy = dict()
        self.__spec_source_files = dict()

    @docval({'name': 'obj_type', 'type': (str, type), 'doc': 'a class name or type object'},
            {'name': 'spec', 'type': BaseStorageSpec, 'doc': 'a Spec object'},
            {'name': 'source_file', 'type': str, 'doc': 'path to the source file from which the spec was loaded', 'default': None})
    def register_spec(self, **kwargs):
        '''
        Associate a specified object type with an HDF5 specification
        '''
        obj_type, spec, source_file = getargs('obj_type', 'spec', 'source_file', kwargs)
        type_name = obj_type.__name__ if isinstance(obj_type, type) else obj_type
        if type_name in self.__specs:
            raise ValueError("'%s' - cannot overwrite existing specification" % type_name)
        self.__specs[type_name] = spec
        self.__spec_source_files[type_name] = source_file
        ndt = spec.neurodata_type
        ndt_def = spec.neurodata_type_def
        if ndt_def != ndt:
            self.__parent_types[ndt_def] = ndt

    @docval({'name': 'obj_type', 'type': (str, type), 'doc': 'a class name or type object'},
            returns="the specification for writing the given object type to HDF5 ", rtype='Spec')
    def get_spec(self, **kwargs):
        '''
        Get the Spec object for the given type
        '''
        obj_type = getargs('obj_type', kwargs)
        type_name = obj_type.__name__ if isinstance(obj_type, type) else obj_type
        return self.__specs.get(type_name, None)

    def get_registered_types(self):
        '''
        Return all registered specifications
        '''
        return tuple(self.__specs.keys())

    @docval({'name': 'obj_type', 'type': (str, type), 'doc': 'a class name or type object'},
            returns="the path to source specification file from which the spec was orignially loaded or None ",
            rtype='str')
    def get_spec_source_file(self, **kwargs):
        '''
        Return the path to the source file from which the spec for the given
        type was loaded from. None is returned if no file path is available
        for the spec. Note: The spec in the file may not be identical to the
        object in case teh spec is modified after load.
        '''
        obj_type = getargs('obj_type', kwargs)
        return self.__spec_source_files.get(obj_type, None)

    @docval({'name': 'spec', 'type': BaseStorageSpec, 'doc': 'the Spec object to register'},
            {'name': 'source_file', 'type': str, 'doc': 'path to the source file from which the spec was loaded', 'default': None})
    def auto_register(self, **kwargs):
        '''
        Register this specification and all sub-specification using neurodata_type as object type name
        '''
        spec, source_file = getargs('spec', 'source_file', kwargs)
        ndt = spec.neurodata_type_def
        if ndt is not None:
            self.register_spec(ndt, spec, source_file)
        for dataset_spec in spec.datasets:
            dset_ndt = dataset_spec.neurodata_type_def
            if dset_ndt is not None:
                self.register_spec(dset_ndt, dataset_spec, source_file)
        for group_spec in spec.groups:
            self.auto_register(group_spec, source_file)

    @docval({'name': 'neurodata_type', 'type': (str, type), 'doc': 'the neurodata_type to get the hierarchy of'})
    def get_hierarchy(self, **kwargs):
        ''' Get the extension hierarchy for the given neurodata_type '''
        neurodata_type = getargs('neurodata_type', kwargs)
        if isinstance(neurodata_type, type):
            neurodata_type = neurodata_type.__name__
        ret = self.__hierarchy.get(neurodata_type)
        if ret is None:
            hierarchy = list()
            parent = neurodata_type
            while parent is not None:
                hierarchy.append(parent)
                parent = self.__parent_types.get(parent)
            # store computed hierarchy for later
            tmp_hier = tuple(hierarchy)
            ret = tmp_hier
            while len(tmp_hier) > 0:
                self.__hierarchy[tmp_hier[0]] = tmp_hier
                tmp_hier = tmp_hier[1:]
        return ret

    def __copy__(self):
        ret = SpecCatalog()
        ret.__specs = copy.copy(spec)
        return ret

    def __deepcopy__(self):
        ret = SpecCatalog()
        ret.__specs = copy.deepcopy(spec)
        return ret

