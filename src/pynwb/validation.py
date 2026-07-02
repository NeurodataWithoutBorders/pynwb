"""Module to validate an NWB file against a namespace."""
from typing import Tuple, List, Dict, Optional
from pathlib import Path
from warnings import warn

from hdmf.spec import NamespaceCatalog
from hdmf.build import BuildManager, TypeMap
from hdmf.utils import docval, getargs, AllowPositional
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


HDF5_OPEN_KEYS = frozenset({"driver", "aws_region", "load_namespaces"})
ZARR_OPEN_KEYS = frozenset({"storage_options"})


def _open_backend_io(path: str,
                     *,
                     backend_kwargs: Optional[dict] = None,
                     manager: Optional[BuildManager] = None) -> HDMFIO:
    # Open an HDMFIO for `path`. `backend_kwargs` may contain a union of
    # HDF5 (Hierarchical Data Format 5) and Zarr open options; this helper
    # resolves the backend via _get_backend and keeps only the keys that apply.
    # Keys whose value is None are dropped, so callers can include all keys
    # unconditionally.
    from pynwb import _get_backend, NWBHDF5IO
    backend_kwargs = backend_kwargs or {}
    backend_io_cls = _get_backend(path, method=backend_kwargs.get("driver"))
    valid_keys = HDF5_OPEN_KEYS if backend_io_cls is NWBHDF5IO else ZARR_OPEN_KEYS
    io_kwargs = {"path": path, "mode": "r"}
    if manager is not None:
        io_kwargs["manager"] = manager
    io_kwargs.update({k: v for k, v in backend_kwargs.items()
                      if k in valid_keys and v is not None})
    return backend_io_cls(**io_kwargs)


def get_cached_namespaces_to_validate(path: Optional[str] = None,
                                      driver: Optional[str] = None,
                                      aws_region: Optional[str] = None,
                                      storage_options: Optional[dict] = None,
                                      io: Optional[HDMFIO] = None,
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
        namespace_dependencies = io.load_namespaces_io(namespace_catalog=catalog)
    else:
        opened_io = _open_backend_io(path, backend_kwargs={
            "driver": driver,
            "aws_region": aws_region,
            "storage_options": storage_options,
        })
        namespace_dependencies = opened_io.load_namespaces_io(namespace_catalog=catalog)
        opened_io.close()

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
    {
        "name": "aws_region",
        "type": str,
        "doc": "AWS region to use when opening the HDF5 file with the ros3 driver.",
        "default": None,
    },
    {
        "name": "storage_options",
        "type": dict,
        "doc": "Zarr storage options for remote stores (used by the Zarr backend).",
        "default": None,
    },
    returns="Validation errors in the file.",
    rtype=list,
    is_method=False,
    allow_positional=AllowPositional.WARNING,
)
def validate(**kwargs):
    """Validate an NWB file against a namespace or its cached namespaces.

    Note: this function checks for compliance with the NWB schema.
    It is recommended to use the NWBInspector for more comprehensive validation of both
    compliance with the schema and compliance of data with NWB best practices.
    """

    io, path, use_cached_namespaces, namespace, verbose, driver, aws_region, storage_options = getargs(
        "io", "path", "use_cached_namespaces", "namespace", "verbose", "driver", "aws_region", "storage_options", kwargs
    )
    assert io != path, "Both 'io' and 'path' were specified! Please choose only one."
    path = str(path) if isinstance(path, Path) else path

    # get namespaces to validate
    namespace_message = "PyNWB namespace information"
    manager = None

    if use_cached_namespaces:
        cached_namespaces, manager, namespace_dependencies = get_cached_namespaces_to_validate(
            path=path, driver=driver, aws_region=aws_region, storage_options=storage_options, io=io,
        )

        if any(cached_namespaces):
            namespaces_to_validate = cached_namespaces
            namespace_message = "cached namespace information"
        else:
            namespaces_to_validate = [CORE_NAMESPACE]
            if verbose:
                warn(f"The file {f'{path} ' if path is not None else ''}has no cached namespace information. "
                     f"Falling back to {namespace_message}.", UserWarning)
    else:
        namespaces_to_validate = [CORE_NAMESPACE]

    # get io object if not provided
    if path is not None:
        io = _open_backend_io(path, backend_kwargs={
            "driver": driver,
            "aws_region": aws_region,
            "storage_options": storage_options,
            "load_namespaces": False if not use_cached_namespaces else None,
        }, manager=manager)

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
