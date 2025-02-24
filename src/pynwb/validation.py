"""Module to validate an NWB file against a namespace."""
from typing import Tuple, List, Dict, Optional
from pathlib import Path
from warnings import warn

from hdmf.spec import NamespaceCatalog
from hdmf.build import BuildManager, TypeMap
from hdmf.utils import docval, getargs, popargs, AllowPositional
from hdmf.backends.io import HDMFIO
from hdmf.validate import ValidatorMap

from pynwb import CORE_NAMESPACE
from pynwb.spec import NWBDatasetSpec, NWBGroupSpec, NWBNamespace


__all__ = [
    'validate',
    'get_cached_namespaces_to_validate'
]

def _validate_helper(io: HDMFIO, namespace: str = CORE_NAMESPACE) -> list:
    builder = io.read_builder()
    validator = ValidatorMap(io.manager.namespace_catalog.get_namespace(name=namespace))
    return validator.validate(builder)


def get_cached_namespaces_to_validate(path: Optional[str] = None, 
                                      driver: Optional[str] = None, 
                                      aws_region: Optional[str] = None,
                                      io: Optional[HDMFIO] = None 
) -> Tuple[List[str], BuildManager, Dict[str, str]]:
    """
    Determine the most specific namespace(s) that are cached in the given NWBFile that can be used for validation.

    Example
    -------
    The following example illustrates how we can use this function to validate against namespaces
    cached in a file. This is useful, e.g., when a file was created using an extension

    .. code-block:: python

        from pynwb import validate
        from pynwb.validation import get_cached_namespaces_to_validate
        path = "my_nwb_file.nwb"
        validate_namespaces, manager, cached_namespaces = get_cached_namespaces_to_validate(path)
        with NWBHDF5IO(path, "r", manager=manager) as reader:
            errors = []
            for ns in validate_namespaces:
                errors += validate(io=reader, namespace=ns)

    :param path: Path for the NWB file
    :return: Tuple with:
      - List of strings with the most specific namespace(s) to use for validation.
      - BuildManager object for opening the file for validation
      - Dict with the full result from NWBHDF5IO.load_namespaces
    """

    catalog = NamespaceCatalog(
        group_spec_cls=NWBGroupSpec, dataset_spec_cls=NWBDatasetSpec, spec_namespace_cls=NWBNamespace
    )

    if io is not None:
        # TODO update HDF5IO to have .file property to make consistent with ZarrIO
        # then update input arguments here
        namespace_dependencies = io.load_namespaces(namespace_catalog=catalog, 
                                                    file=io._file)
    else:
        from pynwb import _get_backend
        backend_io = _get_backend(path, method=driver)
        namespace_dependencies = backend_io.load_namespaces(namespace_catalog=catalog, 
                                                            path=path, 
                                                            driver=driver, 
                                                            aws_region=aws_region)

    # Determine which namespaces are the most specific (i.e. extensions) and validate against those
    candidate_namespaces = set(namespace_dependencies.keys())
    for namespace_dependency in namespace_dependencies:
        candidate_namespaces -= namespace_dependencies[namespace_dependency].keys()

    # TODO: remove this workaround for issue https://github.com/NeurodataWithoutBorders/pynwb/issues/1357
    candidate_namespaces.discard("hdmf-experimental")  # remove validation of hdmf-experimental for now
    cached_namespaces = sorted(candidate_namespaces)

    if len(cached_namespaces) > 0:
        type_map = TypeMap(namespaces=catalog)
        manager = BuildManager(type_map=type_map)
    else:
        manager = None

    return cached_namespaces, manager, namespace_dependencies

@docval(
    {
        "name": "io",
        "type": HDMFIO,
        "doc": "An open IO to an NWB file.",
        "default": None,
    },  # For back-compatability
    {
        "name": "namespace",
        "type": str,
        "doc": "A specific namespace to validate against.",
        "default": None,
    },  # Argument order is for back-compatability
    {
         "name": "paths",
         "type": list,
         "doc": ("List of NWB file paths. This argument will be deprecated in PyNWB 4.0. "
                 "Use 'path' instead."),
         "default": None,
    },
    {
        "name": "path",
        "type": (str, Path),
        "doc": "NWB file path.",
        "default": None,
    },
    {
        "name": "use_cached_namespaces",
        "type": bool,
        "doc": "Whether to use namespaces cached within the file for validation.",
        "default": True,
    },
    {
        "name": "verbose",
        "type": bool,
        "doc": "Whether or not to print messages to stdout.",
        "default": False,
    },
    {
        "name": "driver",
        "type": str,
        "doc": "Driver for h5py to use when opening the HDF5 file.",
        "default": None,
    }, 
    returns="Validation errors in the file.",
    rtype=list,
    is_method=False,
    allow_positional=AllowPositional.WARNING,
)
def validate(**kwargs):
    """Validate NWB file(s) against a namespace or its cached namespaces.

    Note: this function checks for compliance with the NWB schema. 
    It is recommended to use the NWBInspector for more comprehensive validation of both
    compliance with the schema and compliance of data with NWB best practices.
    """

    paths, path = popargs("paths", "path", kwargs)

    if paths is not None:
        warn("The 'paths' argument will be deprecated in PyNWB 4.0 "
            "Use 'path' instead. To migrate, call this function separately for "
            "each path instead of passing a list.",
            DeprecationWarning)

        if path is not None:
            raise ValueError("Both 'paths' and 'path' were specified. "
                             "Please choose only one.")

        validation_errors = []
        for p in paths:
            validation_errors +=  _validate_single_file(path=p, **kwargs)
    else:
        validation_errors = _validate_single_file(path=path, **kwargs)

    return validation_errors


def _validate_single_file(**kwargs):

    io, path, use_cached_namespaces, namespace, verbose, driver = getargs(
        "io", "path", "use_cached_namespaces", "namespace", "verbose", "driver", kwargs
    )
    assert io != path, "Both 'io' and 'path' were specified! Please choose only one."
    path = str(path) if isinstance(path, Path) else path

    # get namespaces to validate
    namespace_message = "PyNWB namespace information"
    io_kwargs = dict(path=path, mode="r", driver=driver)
        
    if use_cached_namespaces:
        cached_namespaces, manager, namespace_dependencies = get_cached_namespaces_to_validate(path=path, 
                                                                                               driver=driver, 
                                                                                               io=io)
        io_kwargs.update(manager=manager)

        if any(cached_namespaces):
            namespaces_to_validate = cached_namespaces
            namespace_message = "cached namespace information"
        else:
            namespaces_to_validate = [CORE_NAMESPACE]
            if verbose:
                warn(f"The file {f'{path} ' if path is not None else ''}has no cached namespace information. "
                     f"Falling back to {namespace_message}.", UserWarning)
    else:
        io_kwargs.update(load_namespaces=False)
        namespaces_to_validate = [CORE_NAMESPACE]

    # get io object if not provided
    if path is not None:
        from pynwb import _get_backend
        backend_io = _get_backend(path, method=driver)
        io = backend_io(**io_kwargs)

    # check namespaces are accurate
    if namespace is not None:
        if namespace in namespaces_to_validate:
            namespaces_to_validate = [namespace]
        elif use_cached_namespaces and namespace in namespace_dependencies:  # validating against a dependency
            for namespace_dependency in namespace_dependencies:
                if namespace in namespace_dependencies[namespace_dependency]:
                    raise ValueError(
                        f"The namespace '{namespace}' is included by the namespace "
                        f"'{namespace_dependency}'. Please validate against that namespace instead.")
        else:
            raise ValueError(
                f"The namespace '{namespace}' could not be found in {namespace_message} as only "
                f"{namespaces_to_validate} is present.",)
  
    # validate against namespaces
    validation_errors = []
    for validation_namespace in namespaces_to_validate:
        if verbose:
            print(f"Validating {f'{path} ' if path is not None else ''}against "  # noqa: T201
                  f"{namespace_message} using namespace '{validation_namespace}'.")  
        validation_errors += _validate_helper(io=io, namespace=validation_namespace)

    if path is not None:
        io.close()  # close the io object if it was created within this function, otherwise leave as is
    
    return validation_errors

