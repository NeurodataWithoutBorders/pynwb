"""Command line tool to Validate an NWB file against a namespace."""
import json
import sys
from argparse import ArgumentParser
from typing import Tuple, List, Dict, Optional
from pathlib import Path
from warnings import warn

from hdmf.spec import NamespaceCatalog
from hdmf.build import BuildManager, TypeMap
from hdmf.utils import docval, getargs
from hdmf.backends.io import HDMFIO
from hdmf.validate import ValidatorMap

from pynwb import CORE_NAMESPACE
from pynwb.spec import NWBDatasetSpec, NWBGroupSpec, NWBNamespace


def _print_errors(validation_errors: list):
    if validation_errors:
        print(" - found the following errors:", file=sys.stderr)
        for err in validation_errors:
            print(str(err), file=sys.stderr)
    else:
        print(" - no errors found.")

def _get_backend(path: str):
    from . import NWBHDF5IO
    from hdmf_zarr import NWBZarrIO

    backend_io_classes = [NWBHDF5IO, NWBZarrIO]
    backend_options = [b for b in backend_io_classes if b.can_read(path=path)]
    if len(backend_options) == 0:
        warn(f"Could not find an IO to read the file '{path}'." 
             f"This may be due to an older file version or invalid file." 
             f"Defaulting to NWBHDF5IO.", UserWarning)
        return NWBHDF5IO
    elif len(backend_options) > 1:
        raise ValueError(f"Multiple backends found for file '{path}': {backend_options}")
    else:
        return backend_options[0]

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
        namespace_dependencies = io.load_namespaces(namespace_catalog=catalog, 
                                                    file=io.file)  # TODO would need to update HDMFIO, ZarrIO to support file input
    else:
        backend_io = _get_backend(path)
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
    rtype=(list, (list, bool)),
    is_method=False,
)
def validate(**kwargs):
    """Validate NWB file(s) against a namespace or its cached namespaces.
    """

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
    if io is None:
        backend_io = _get_backend(path)
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
            print(f"Validating {f'{path} ' if path is not None else ''}against "
                  f"{namespace_message} using namespace '{validation_namespace}'.")
        validation_errors += _validate_helper(io=io, namespace=validation_namespace)

    return validation_errors


def validate_cli():
    """CLI wrapper around pynwb.validate."""
    parser = ArgumentParser(
        description="Validate an NWB file",
        epilog="If --ns is not specified, validate against all namespaces in the NWB file.",
    )

    # Special arg specific to CLI
    parser.add_argument(
        "-lns",
        "--list-namespaces",
        dest="list_namespaces",
        action="store_true",
        help="List the available namespaces and exit.",
    )

    # Common args to the API validate
    parser.add_argument("path", type=str, help="NWB file path")
    parser.add_argument("-n", "--ns", type=str, help="the namespace to validate against")
    parser.add_argument("--json-file-path", dest="json_file_path", type=str, help="Write json output to this location.")
    feature_parser = parser.add_mutually_exclusive_group(required=False)
    feature_parser.add_argument(
        "--no-cached-namespace",  # NOTE - update to match validate inputs?
        dest="no_cached_namespace",
        action="store_true",
        help="Use the PyNWB loaded namespace (true) or use the cached namespace (false; default).",
    )
    parser.set_defaults(no_cached_namespace=False)
    args = parser.parse_args()

    if args.list_namespaces:
        cached_namespaces, _, _ = get_cached_namespaces_to_validate(path=args.path)
        print("\n".join(cached_namespaces))
        status = 0
    else:
        validation_errors = []
        try:
            validation_errors = validate(
                path=args.path, use_cached_namespaces=not args.no_cached_namespace, namespace=args.ns, verbose=True, 
            )
            _print_errors(validation_errors=validation_errors)
            status = validation_errors is not None and len(validation_errors) > 0
        except ValueError as e:
            print(e, file=sys.stderr)
            status = 1
        
    # write output to json file
    if args.json_file_path is not None:
        with open(args.json_file_path, "w") as f:
            json_report = {'status': int(status), 'validation_errors': [str(e) for e in validation_errors]}
            json.dump(obj=json_report, fp=f)
            print(f"Report saved to {str(Path(args.json_file_path).absolute())}!")

    sys.exit(status)


if __name__ == "__main__":  # pragma: no cover
    validate_cli()
