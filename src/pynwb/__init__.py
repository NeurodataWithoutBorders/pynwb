'''This package will contain functions, classes, and objects
for reading and writing data in NWB format
'''
import os.path
from pathlib import Path
from copy import deepcopy
import subprocess
import pickle
from warnings import warn
from platformdirs import PlatformDirs
import h5py

import hdmf
from hdmf.spec import NamespaceCatalog
from hdmf.utils import docval, getargs, popargs, get_docval
from hdmf.backends.io import HDMFIO
from hdmf.backends.hdf5 import HDF5IO as _HDF5IO
from hdmf.build import BuildManager, TypeMap
import hdmf.common
from hdmf.common import load_type_config as hdmf_load_type_config
from hdmf.common import get_loaded_type_config as hdmf_get_loaded_type_config
from hdmf.common import unload_type_config as hdmf_unload_type_config


CORE_NAMESPACE = 'core'

from .spec import NWBDatasetSpec, NWBGroupSpec, NWBNamespace  # noqa E402
from .validation import validate  # noqa: F401, E402

try:
    # see https://effigies.gitlab.io/posts/python-packaging-2023/
    from ._version import __version__
except ImportError:  # pragma: no cover
    # this is a relatively slower method for getting the version string
    from importlib.metadata import version  # noqa: E402

    __version__ = version("pynwb")
    del version


@docval({'name': 'config_path', 'type': str, 'doc': 'Path to the configuration file.'},
        {'name': 'type_map', 'type': TypeMap, 'doc': 'The TypeMap.', 'default': None},
        is_method=False)
def load_type_config(**kwargs):
    """
    This method will either load the default config or the config provided by the path.
    """
    config_path = kwargs['config_path']
    type_map = kwargs['type_map'] or get_type_map()

    hdmf_load_type_config(config_path=config_path, type_map=type_map)

@docval({'name': 'type_map', 'type': TypeMap, 'doc': 'The TypeMap.', 'default': None},
        is_method=False)
def get_loaded_type_config(**kwargs):
    type_map = kwargs['type_map'] or get_type_map()
    return hdmf_get_loaded_type_config(type_map=type_map)

@docval({'name': 'type_map', 'type': TypeMap, 'doc': 'The TypeMap.', 'default': None},
        is_method=False)
def unload_type_config(**kwargs):
    """
    Remove validation.
    """
    type_map = kwargs['type_map'] or get_type_map()
    hdmf_unload_type_config(type_map=type_map)

def __get_resources() -> dict:
    from importlib.resources import files

    __location_of_this_file = files(__name__)
    __core_ns_file_name = 'nwb.namespace.yaml'
    __schema_dir = 'nwb-schema/core'

    # create a cache directory for the core typemap
    dirs = PlatformDirs(appname="pynwb-hdmf", version=f"{__version__}-{hdmf.__version__}", ensure_exists=True)
    cache_dir = dirs.user_cache_path
    cached_core_typemap = cache_dir / 'pynwb_core_typemap.pkl'

    ret = dict()
    ret['namespace_path'] = str(__location_of_this_file / __schema_dir / __core_ns_file_name)
    ret['cached_typemap_path'] = str(cached_core_typemap)
    ret['user_cache_dir'] = str(dirs.user_cache_dir)
    return ret



# a global type map
global __TYPE_MAP

__ns_catalog = NamespaceCatalog(NWBGroupSpec, NWBDatasetSpec, NWBNamespace, core_namespaces=[CORE_NAMESPACE])

hdmf_typemap = hdmf.common.get_type_map()
__TYPE_MAP = TypeMap(__ns_catalog)
__TYPE_MAP.merge(hdmf_typemap, ns_catalog=True)

# load the core namespace, i.e. base NWB specification
__resources = __get_resources()


@docval({'name': 'extensions', 'type': (str, TypeMap, list),
         'doc': 'a path to a namespace, a TypeMap, or a list consisting of paths to namespaces and TypeMaps',
         'default': None},
        returns="TypeMap loaded for the given extension or NWB core namespace", rtype=tuple,
        is_method=False)
def get_type_map(**kwargs):
    '''
    Get the TypeMap for the given extensions. If no extensions are provided,
    return the TypeMap for the core namespace
    '''
    extensions = getargs('extensions', kwargs)
    type_map = None
    if extensions is None:
        type_map = deepcopy(__TYPE_MAP)
    else:
        if isinstance(extensions, TypeMap):
            type_map = extensions
        else:
            type_map = deepcopy(__TYPE_MAP)
        if isinstance(extensions, list):
            for ext in extensions:
                if isinstance(ext, str):
                    type_map.load_namespaces(ext)
                elif isinstance(ext, TypeMap):
                    type_map.merge(ext)
                else:
                    raise ValueError('extensions must be a list of paths to namespace specs or a TypeMaps')
        elif isinstance(extensions, str):
            type_map.load_namespaces(extensions)
        elif isinstance(extensions, TypeMap):
            type_map.merge(extensions)
    return type_map


@docval(*get_docval(get_type_map),
        returns="the namespaces loaded from the given file", rtype=tuple,
        is_method=False)
def get_manager(**kwargs):
    '''
    Get a BuildManager to use for I/O using the given extensions. If no extensions are provided,
    return a BuildManager that uses the core namespace
    '''
    type_map = get_type_map(**kwargs)
    return BuildManager(type_map)


@docval({'name': 'namespace_path', 'type': str, 'doc': 'the path to the YAML with the namespace definition'},
        returns="the namespaces loaded from the given file", rtype=tuple,
        is_method=False)
def load_namespaces(**kwargs):
    '''
    Load namespaces from file
    '''
    namespace_path = getargs('namespace_path', kwargs)
    return __TYPE_MAP.load_namespaces(namespace_path)


def available_namespaces():
    """Returns all namespaces registered in the namespace catalog"""
    return __TYPE_MAP.namespace_catalog.namespaces


def __git_cmd(*args) -> subprocess.CompletedProcess:
    """
    Call git with the package as the directory regardless of cwd.

    Since any folder within a git repo works, don't try to ascend to the top, since
    if we're *not* actually in a git repo we're only guaranteed to know about
    the inner `pynwb` directory.
    """
    parent_dir = str(Path(__file__).parent)
    result = subprocess.run(["git", "-C", parent_dir, *args], capture_output=True)
    return result


def __clone_submodules():
    if __git_cmd('rev-parse').returncode == 0:
        warn(
            'NWB core schema not found in cloned installation, initializing submodules...',
            stacklevel=1)
        res = __git_cmd('submodule', 'update', '--init', '--recursive')
        if not res.returncode == 0:  # pragma: no cover
            raise RuntimeError(
                'Exception while initializing submodules, got:\n'
                'stdout:\n' + ('-'*20) + res.stdout + "\nstderr:\n" + ('-'*20) + res.stderr)
    else:  # pragma: no cover
        raise RuntimeError("Package is not installed from a git repository, can't clone submodules")

def clear_cache_dir():
    """
    Clear all the cached typemap files for all versions
    """
    try:
        for f in Path(__resources['user_cache_dir']).parent.glob('**/pynwb_core_typemap.pkl'):
            Path(f).unlink()
    except (OSError, PermissionError) as e:
        warn(f'Could not clear cache directory: {e}', UserWarning)

def __load_core_namespace(final:bool=False):
    """
    Load the core namespace into __TYPE_MAP,
    either by loading a pickled version or creating one anew and pickling it.

    We keep a dotfile next to it that tracks what version of pynwb created it,
    so that we invalidate it when the code changes.

    Args:
        final (bool): This function tries again if the submodules aren't cloned,
            but it shouldn't go into an infinite loop.
            If final is ``True``, don't recurse.
    """
    global __TYPE_MAP
    global __resources

    # Check for environment variable to disable caching
    disable_cache = os.environ.get('PYNWB_NO_CACHE_DIR', '0') == '1'

    # load pickled typemap if we have one and want to use caching
    if os.path.exists(__resources['cached_typemap_path']) and not disable_cache:
        with open(__resources['cached_typemap_path'], 'rb') as f:
            __TYPE_MAP = pickle.load(f)  # type: TypeMap

    # otherwise make a new one and cache it
    elif os.path.exists(__resources['namespace_path']):
        load_namespaces(__resources['namespace_path'])

        # cache the loaded namespace if caching is not disabled
        if not disable_cache:
            try:
                with open(__resources['cached_typemap_path'], 'wb') as f:
                    pickle.dump(__TYPE_MAP, f, protocol=pickle.HIGHEST_PROTOCOL)
            except (OSError, PermissionError):
                pass  # skip caching if we can't write the cached typemap
    # otherwise, we don't have the schema and try and initialize from submodules,
    # afterwards trying to load the namespace again
    else:
        try:
            __clone_submodules()
        except (FileNotFoundError, OSError, RuntimeError) as e:  # pragma: no cover
            if 'core' not in available_namespaces():
                warn(
                    "'core' is not a registered namespace. If you installed PyNWB locally using a git clone, "
                    "you need to use the --recurse_submodules flag when cloning. "
                    "See developer installation instructions here: "
                    "https://pynwb.readthedocs.io/en/stable/install_developers.html#install-from-git-repository\n"
                    f"Got exception: \n{e}"
                )
        if not final:
            __load_core_namespace(final=True)
__load_core_namespace()


# a function to register a container classes with the global map
@docval({'name': 'neurodata_type', 'type': str, 'doc': 'the neurodata_type to get the spec for'},
        {'name': 'namespace', 'type': str, 'doc': 'the name of the namespace'},
        {"name": "container_cls", "type": type, "doc": "the class to map to the specified neurodata_type",
         'default': None},
        is_method=False)
def register_class(**kwargs):
    """Register an NWBContainer class to use for reading and writing a neurodata_type from a specification
    If container_cls is not specified, returns a decorator for registering an NWBContainer subclass
    as the class for neurodata_type in namespace.
    """
    neurodata_type, namespace, container_cls = getargs('neurodata_type', 'namespace', 'container_cls', kwargs)

    def _dec(cls):
        __TYPE_MAP.register_container_type(namespace, neurodata_type, cls)
        return cls
    if container_cls is None:
        return _dec
    else:
        _dec(container_cls)


@docval({'name': 'h5py_file', 'type': h5py.File, 'doc': 'An NWB file'}, rtype=tuple,
        is_method=False,)
def get_nwbfile_version(**kwargs):
    """
    Get the NWB version of the file if it is an NWB file.

    :Returns: Tuple consisting of: 1) the
        original version string as stored in the file and 2) a tuple with the parsed components of the version string,
        consisting of integers and strings, e.g., (2, 5, 1, beta). (None, None) will be returned if the file is not a
        valid NWB file or the nwb_version is missing, e.g., in the case when no data has been written to the file yet.
    """
    # Get the version string for the NWB file
    h5py_file = getargs('h5py_file', kwargs)
    try:
        nwb_version_string = h5py_file.attrs['nwb_version']
    #  KeyError occurs  when the file is empty (e.g., when creating a new file nothing has been written)
    #  or when the HDF5 file is not a valid NWB file
    except KeyError:
        return None, None
    # Other system may have written nwb_version as a fixed-length string, resulting in a numpy.bytes_ object
    # on read, rather than a variable-length string. To address this, decode the bytes if necessary.
    if not isinstance(nwb_version_string, str):
        nwb_version_string = nwb_version_string.decode()

    # Parse the version string
    nwb_version_parts = nwb_version_string.replace("-", ".").replace("_", ".").split(".")
    nwb_version = tuple([int(i) if i.isnumeric() else i
                         for i in nwb_version_parts])
    return nwb_version_string, nwb_version


# a function to register an object mapper for a container class
@docval({"name": "container_cls", "type": type,
         "doc": "the Container class for which the given ObjectMapper class gets used"},
        {"name": "mapper_cls", "type": type, "doc": "the ObjectMapper class to use to map", 'default': None},
        is_method=False)
def register_map(**kwargs):
    """Register an ObjectMapper to use for a Container class type
    If mapper_cls is not specified, returns a decorator for registering an ObjectMapper class as the mapper for
    container_cls. If mapper_cls is specified, register the class as the mapper for container_cls
    """
    container_cls, mapper_cls = getargs('container_cls', 'mapper_cls', kwargs)

    def _dec(cls):
        __TYPE_MAP.register_map(container_cls, cls)
        return cls
    if mapper_cls is None:
        return _dec
    else:
        _dec(mapper_cls)


@docval({'name': 'neurodata_type', 'type': str, 'doc': 'the neurodata_type to get the NWBContainer class for'},
        {'name': 'namespace', 'type': str, 'doc': 'the namespace the neurodata_type is defined in'},
        is_method=False)
def get_class(**kwargs):
    """
    Parse the YAML file for a given neurodata_type that is a subclass of NWBContainer and automatically generate its
    python API. This will work for most containers, but is known to not work for descendants of MultiContainerInterface
    and DynamicTable, so these must be defined manually (for now). `get_class` infers the API mapping directly from the
    specification. If you want to define a custom mapping, you should not use this function and you should define the
    class manually.

    Examples:

    Generating and registering an extension is as simple as::

        MyClass = get_class('MyClass', 'ndx-my-extension')

    `get_class` defines only the `__init__` for the class. In cases where you want to provide additional methods for
    querying, plotting, etc. you can still use `get_class` and attach methods to the class after-the-fact, e.g.::

        def get_sum(self, a, b):
            return self.feat1 + self.feat2

        MyClass.get_sum = get_sum

    """
    neurodata_type, namespace = getargs('neurodata_type', 'namespace', kwargs)
    return __TYPE_MAP.get_dt_container_cls(neurodata_type, namespace)


@docval({'name': 'path', 'type': str, 'doc': 'Path to the NWB file which can be an HDF5 file or a Zarr store.'},
        {"name": "method", "type": str, "doc": "the method to use when opening the file", 'default': None},
        is_method=False)
def _get_backend(path: str, method: str = None):
    if method == "ros3":
        return NWBHDF5IO  # TODO - add additional conditions for other streaming methods

    try:
        from hdmf_zarr import NWBZarrIO
        backend_io_classes = [NWBHDF5IO, NWBZarrIO]
    except ImportError:
        backend_io_classes = [NWBHDF5IO]

    backend_options = [b for b in backend_io_classes if b.can_read(path=path)]
    if len(backend_options) == 0:
        raise ValueError(f"Could not find an IO to read the file '{path}'. If you are trying to read "
                         f"a Zarr file, make sure you have hdmf-zarr installed.")
    else:
        return backend_options[0]


class NWBHDF5IO(_HDF5IO):

    @staticmethod
    def can_read(path: str):
        """Determine whether a given path is readable by this class"""
        if not os.path.isfile(path):  # path is file that exists
            return False
        try:
            with h5py.File(path, "r") as file:   # path is HDF5 file
                version_info = get_nwbfile_version(file)
                if version_info[0] is None:
                    warn("Cannot read because missing NWB version in the HDF5 file. The file is not a valid NWB file.")
                    return False
                elif version_info[1][0] < 2:    # Major versions of NWB < 2 not supported
                    warn("Cannot read because PyNWB supports NWB files version 2 and above.")
                    return False
                else:
                    return True
        except IOError:
            return False

    @docval({'name': 'path', 'type': (str, Path), 'doc': 'the path to the HDF5 file', 'default': None},
            {'name': 'mode', 'type': str,
             'doc': 'the mode to open the HDF5 file with, one of ("w", "r", "r+", "a", "w-", "x")',
             'default': 'r'},
            {'name': 'load_namespaces', 'type': bool,
             'doc': ('whether or not to load cached namespaces from given path - not applicable in write mode '
                     'or when `manager` is not None or when `extensions` is not None'),
             'default': True},
            {'name': 'manager', 'type': BuildManager, 'doc': 'the BuildManager to use for I/O', 'default': None},
            {'name': 'extensions', 'type': (str, TypeMap, list),
             'doc': 'a path to a namespace, a TypeMap, or a list consisting paths to namespaces and TypeMaps',
             'default': None},
            *get_docval(_HDF5IO.__init__, "file", "comm", "driver", "aws_region", "herd_path"),)
    def __init__(self, **kwargs):
        path, mode, manager, extensions, load_namespaces, file_obj, comm, driver, aws_region, herd_path =\
            popargs('path', 'mode', 'manager', 'extensions', 'load_namespaces',
                    'file', 'comm', 'driver', 'aws_region', 'herd_path', kwargs)
        # Define the BuildManager to use
        io_modes_that_create_file = ['w', 'w-', 'x']
        if mode in io_modes_that_create_file or manager is not None or extensions is not None:
            load_namespaces = False

        if mode in io_modes_that_create_file and not str(path).endswith('.nwb'):
            warn(f"The file path provided: {path} does not end in '.nwb'. "
                 "It is recommended that NWB files using the HDF5 backend use the '.nwb' extension.", UserWarning)

        if load_namespaces:
            tm = get_type_map()
            super().load_namespaces(tm, path, file=file_obj, driver=driver, aws_region=aws_region)
            manager = BuildManager(tm)

            # XXX: Leaving this here in case we want to revert to this strategy for
            #      loading cached namespaces
            # ns_catalog = NamespaceCatalog(NWBGroupSpec, NWBDatasetSpec, NWBNamespace)
            # super().load_namespaces(ns_catalog, path)
            # tm = TypeMap(ns_catalog)
            # tm.copy_mappers(get_type_map())
        else:
            if manager is not None and extensions is not None:
                raise ValueError("'manager' and 'extensions' cannot be specified together")
            elif extensions is not None:
                manager = get_manager(extensions=extensions)
            elif manager is None:
                manager = get_manager()
        # Open the file
        super().__init__(path, manager=manager, mode=mode, file=file_obj, comm=comm,
                         driver=driver, aws_region=aws_region, herd_path=herd_path)

    @property
    def nwb_version(self):
        """
        Get the version of the NWB file opened via this NWBHDF5IO object.

        :returns: Tuple consisting of: 1) the original version string as stored in the file and
                  2) a tuple with the parsed components of the version string, consisting of integers
                  and strings, e.g., (2, 5, 1, beta). (None, None) will be returned if the nwb_version
                  is missing, e.g., in the case when no data has been written to the file yet.
        """
        return get_nwbfile_version(self._file)

    @docval(*get_docval(_HDF5IO.read),
            {'name': 'skip_version_check', 'type': bool, 'doc': 'skip checking of NWB version', 'default': False})
    def read(self, **kwargs):
        """
        Read the NWB file from the IO source.

        :raises TypeError: If the NWB file version is missing or not supported

        :return: NWBFile container
        """
        # Check that the NWB file is supported
        skip_verison_check = popargs('skip_version_check', kwargs)
        if not skip_verison_check:
            file_version_str, file_version = self.nwb_version
            if file_version is None:
                raise TypeError("Missing NWB version in file. The file is not a valid NWB file.")
            if file_version[0] < 2:
                raise TypeError("NWB version %s not supported. PyNWB supports NWB files version 2 and above." %
                                str(file_version_str))
        # read the file
        file = super().read(**kwargs)
        return file

    @docval({'name': 'src_io', 'type': HDMFIO,
             'doc': 'the HDMFIO object (such as NWBHDF5IO) that was used to read the data to export'},
            {'name': 'nwbfile', 'type': 'NWBFile',
             'doc': 'the NWBFile object to export. If None, then the entire contents of src_io will be exported',
             'default': None},
            {'name': 'write_args', 'type': dict,
             'doc': 'arguments to pass to :py:meth:`~hdmf.backends.io.HDMFIO.write_builder`',
             'default': None},
            {'name': 'cache_spec', 'type': bool, 'doc': 'whether to cache the specification to file',
             'default': True})
    def export(self, **kwargs):
        """
        Export an NWB file to a new NWB file using the HDF5 backend.

        If ``nwbfile`` is provided, then the build manager of ``src_io`` is used to build the container,
        and the resulting builder will be exported to the new backend. So if ``nwbfile`` is provided,
        ``src_io`` must have a non-None manager property. If ``nwbfile`` is None, then the contents of
        ``src_io`` will be read and exported to the new backend.

        Arguments can be passed in for the ``write_builder`` method using ``write_args``. Some arguments may not be
        supported during export. ``{'link_data': False}`` can be used to copy any datasets linked to from
        the original file instead of creating a new link to those datasets in the exported file.

        The exported file will not contain any links to the original file. All links, internal and external,
        will be preserved in the exported file. All references will also be preserved in the exported file.

        The exported file will use the latest schema version supported by the version of PyNWB used. For example, if
        the input file uses the NWB schema version 2.1 and the latest schema version supported by PyNWB is 2.3,
        then the exported file will use the 2.3 NWB schema.

        Example usage:

        .. code-block:: python

           with NWBHDF5IO(self.read_path, mode='r') as read_io:
               nwbfile = read_io.read()
               # ...  # modify nwbfile
               nwbfile.set_modified()  # this may be necessary if the modifications are changes to attributes

               with NWBHDF5IO(self.export_path, mode='w') as export_io:
                   export_io.export(src_io=read_io, nwbfile=nwbfile)

        See :ref:`export` and :ref:`modifying_data` for more information and examples.
        """
        nwbfile = popargs('nwbfile', kwargs)
        kwargs['container'] = nwbfile
        super().export(**kwargs)

    @staticmethod
    @docval({'name': 'path', 'type': (str, Path), 'doc': 'the path to the HDF5 file', 'default': None},
            {'name': 'file', 'type': [h5py.File, 'S3File'], 'doc': 'a pre-existing h5py.File object', 'default': None},
            is_method=False)
    def read_nwb(**kwargs):
        """
        Helper factory method for reading an NWB file and return the NWBFile object
        """
        # Retrieve the filepath
        path = popargs('path', kwargs)
        file = popargs('file', kwargs)
        
        path = str(path) if path is not None else None

        # Streaming case
        if path is not None and (path.startswith("s3://") or path.startswith("http")):
            import fsspec
            fsspec_file_system = fsspec.filesystem("http")
            ffspec_file = fsspec_file_system.open(path, "rb")

            open_file = h5py.File(ffspec_file, "r")
            io = NWBHDF5IO(file=open_file)
            nwbfile = io.read()
        else:
            io = NWBHDF5IO(path=path, file=file, mode="r", load_namespaces=True)
            nwbfile = io.read()

        return nwbfile

@docval({'name': 'path', 'type': (str, Path), 
         'doc': 'Path to the NWB file. Can be either a local filesystem path to '
                'an HDF5 (.nwb) or Zarr (.zarr) file.'}, 
        is_method=False)
def read_nwb(**kwargs):
    """Read an NWB file from a local path.

    High-level interface for reading NWB files. Automatically handles both HDF5 
    and Zarr formats. For advanced use cases (parallel I/O, custom namespaces), 
    use NWBHDF5IO or NWBZarrIO.

    See also 
        * :py:class:`~pynwb.NWBHDF5IO`: Core I/O class for HDF5 files with advanced options.
        * :py:class:`~hdmf_zarr.nwb.NWBZarrIO`: Core I/O class for Zarr files with advanced options.

    Notes
        This function uses the following defaults:
            * Always opens in read-only mode
            * Automatically loads namespaces
            * Reads any backend (e.g. HDF5 or Zarr) if there is an IO class available.

        Advanced features requiring direct use of IO classes (e.g. NWBHDF5IO NWBZarrIO) include:
            * Streaming data from s3
            * Custom namespace extensions
            * Parallel I/O with MPI
            * Custom build managers
            * Write or append modes
            * Pre-opened HDF5 file objects or Zarr stores
            * Remote file access configuration
 
    Example usage reading a local NWB file:

    .. code-block:: python

        from pynwb import read_nwb
        nwbfile = read_nwb("path/to/file.nwb")    

    :Returns: pynwb.NWBFile The loaded NWB file object.
    """
    
    path = popargs('path', kwargs)
    # HDF5 is always available so we try that first
    backend_is_hdf5 = NWBHDF5IO.can_read(path=path)
    if backend_is_hdf5:
        return NWBHDF5IO.read_nwb(path=path)
    else:
        # If hdmf5 zarr is available we try that next
        try:
            from hdmf_zarr import NWBZarrIO
            backend_is_zarr = NWBZarrIO.can_read(path=path)
            if backend_is_zarr:
                return NWBZarrIO.read_nwb(path=path) 
            else:
                raise ValueError(
                    f"Unable to read file: '{path}'. The file is not recognized as "
                    "either a valid HDF5 or Zarr NWB file. Please ensure the file exists and contains valid NWB data."
                )     
        except ImportError:
            raise ValueError(
                f"Unable to read file: '{path}'. The file is not recognized as an HDF5 NWB file. "
                "If you are trying to read a Zarr file, please install hdmf-zarr using: pip install hdmf-zarr"
            )
    


from . import io as __io  # noqa: F401,E402
from .core import NWBContainer, NWBData  # noqa: F401,E402
from .base import TimeSeries, ProcessingModule  # noqa: F401,E402
from .file import NWBFile  # noqa: F401,E402
from . import behavior  # noqa: F401,E402
from . import device  # noqa: F401,E402
from . import ecephys  # noqa: F401,E402
from . import epoch  # noqa: F401,E402
from . import icephys  # noqa: F401,E402
from . import image  # noqa: F401,E402
from . import misc  # noqa: F401,E402
from . import ogen  # noqa: F401,E402
from . import ophys  # noqa: F401,E402
from . import legacy  # noqa: F401,E402
from hdmf.data_utils import DataChunkIterator  # noqa: F401,E402
from hdmf.backends.hdf5 import H5DataIO  # noqa: F401,E402

__all__ = [
    # Functions
    'get_type_map',
    'get_manager',
    'load_namespaces', 
    'available_namespaces',
    'clear_cache_dir',
    'register_class',
    'register_map',
    'get_class',
    'load_type_config',
    'get_loaded_type_config',
    'unload_type_config',
    'read_nwb',
    'get_nwbfile_version',
    
    # Classes
    'NWBHDF5IO',
    'NWBContainer',
    'NWBData', 
    'TimeSeries',
    'ProcessingModule',
    'NWBFile',
    'DataChunkIterator',
    'H5DataIO'
]



from ._due import due, BibTeX  # noqa: E402
due.cite(
    BibTeX("""
@article {10.7554/eLife.78362,
article_type = {journal},
title = {{The Neurodata Without Borders ecosystem for neurophysiological data science}},
author = {R\"ubel, Oliver and Tritt, Andrew and Ly, Ryan and Dichter, Benjamin K and
          Ghosh, Satrajit and Niu, Lawrence and Baker, Pamela and Soltesz, Ivan and Ng,
          Lydia and Svoboda, Karel and Frank, Loren and Bouchard, Kristofer E},
editor = {Colgin, Laura L and Jadhav, Shantanu P},
volume = {11},
year = {2022},
month = {oct},
pub_date = {2022-10-04},
pages = {e78362},
citation = {eLife 2022;11:e78362},
doi = {10.7554/eLife.78362},
url = {https://doi.org/10.7554/eLife.78362},
keywords = {Neurophysiology, data ecosystem, data language, data standard, FAIR data, archive},
journal = {eLife},
issn = {2050-084X},
publisher = {eLife Sciences Publications, Ltd}}
"""),
    description="The Neurodata Without Borders ecosystem for neurophysiological data science",
    path="pynwb/", version=__version__,
    cite_module=True
)
del due, BibTeX
