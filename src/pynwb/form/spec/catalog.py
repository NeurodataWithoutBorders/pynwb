from collections import OrderedDict

from .spec import BaseStorageSpec, GroupSpec
from ..utils import docval, getargs


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
        self.__specs = OrderedDict()
        self.__parent_types = dict()
        self.__hierarchy = dict()
        self.__spec_source_files = dict()

    @docval({'name': 'spec', 'type': BaseStorageSpec, 'doc': 'a Spec object'},
            {'name': 'source_file', 'type': str,
             'doc': 'path to the source file from which the spec was loaded', 'default': None})
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

    @docval(rtype=tuple)
    def get_registered_types(self, **kwargs):
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
            {'name': 'source_file',
             'type': str,
             'doc': 'path to the source file from which the spec was loaded', 'default': None},
            rtype=tuple, returns='the types that were registered with this spec')
    def auto_register(self, **kwargs):
        '''
        Register this specification and all sub-specification using data_type as object type name
        '''
        spec, source_file = getargs('spec', 'source_file', kwargs)
        ndt = spec.data_type_def
        ret = list()
        if ndt is not None:
            self.register_spec(spec, source_file)
            ret.append(ndt)
        if isinstance(spec, GroupSpec):
            for dataset_spec in spec.datasets:
                dset_ndt = dataset_spec.data_type_def
                if dset_ndt is not None and not spec.is_inherited_type(dataset_spec):
                    ret.append(dset_ndt)
                    self.register_spec(dataset_spec, source_file)
            for group_spec in spec.groups:
                ret.extend(self.auto_register(group_spec, source_file))
        return tuple(ret)

    @docval({'name': 'data_type', 'type': (str, type),
             'doc': 'the data_type to get the hierarchy of'})
    def get_hierarchy(self, **kwargs):
        ''' Get the extension hierarchy for the given data_type '''
        data_type = getargs('data_type', kwargs)
        if isinstance(data_type, type):
            data_type = data_type.__name__
        ret = self.__hierarchy.get(data_type)
        if ret is None:
            hierarchy = list()
            parent = data_type
            while parent is not None:
                hierarchy.append(parent)
                parent = self.__parent_types.get(parent)
            # store computed hierarchy for later
            tmp_hier = tuple(hierarchy)
            ret = tmp_hier
            while len(tmp_hier) > 0:
                self.__hierarchy[tmp_hier[0]] = tmp_hier
                tmp_hier = tmp_hier[1:]
        return tuple(ret)

    def __copy__(self):
        ret = SpecCatalog()
        ret.__specs = copy.copy(spec)  # noqa: F821
        return ret

    def __deepcopy__(self):
        ret = SpecCatalog()
        ret.__specs = copy.deepcopy(spec)  # noqa: F821
        return ret
