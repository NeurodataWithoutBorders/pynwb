"""Command line tool to Validate an NWB file against a namespace."""
import sys
from argparse import ArgumentParser
from typing import Tuple, List, Dict

from hdmf.spec import NamespaceCatalog
from hdmf.build import BuildManager
from hdmf.build import TypeMap as TypeMap
from hdmf.utils import docval, getargs
from hdmf.backends.io import HDMFIO
from hdmf.validate import ValidatorMap

from pynwb import CORE_NAMESPACE
from pynwb.spec import NWBDatasetSpec, NWBGroupSpec, NWBNamespace


def _check_errors(validation_errors: list) -> bool:
    return validation_errors is not None and len(validation_errors) > 0


def _print_errors(validation_errors: list):
    if validation_errors:
        print(" - found the following errors:", file=sys.stderr)
        for err in validation_errors:
            print(str(err), file=sys.stderr)
    else:
        print(" - no errors found.")


def _validate_helper(io: HDMFIO, namespace: str = CORE_NAMESPACE) -> list:
    builder = io.read_builder()
    validator = ValidatorMap(io.manager.namespace_catalog.get_namespace(name=namespace))
    return validator.validate(builder)


def _get_cached_namespaces_to_validate(path: str) -> Tuple[List[str], BuildManager, Dict[str, str]]:
    """
    Determine the most specific namespace(s) that are cached in the given NWBFile that can be used for validation.

    Example
    -------
    The following example illustrates how we can use this function to validate against namespaces
    cached in a file. This is useful, e.g., when a file was created using an extension
    >>> from pynwb import validate
    >>> from pynwb.validate import _get_cached_namespaces_to_validate
    >>> path = "my_nwb_file.nwb"
    >>> validate_namespaces, manager, cached_namespaces = _get_cached_namespaces_to_validate(path)
    >>> with NWBHDF5IO(path, "r", manager=manager) as reader:
    >>>     errors = []
    >>>     for ns in validate_namespaces:
    >>>         errors += validate(io=reader, namespace=ns)
    :param path: Path for the NWB file
    :return: Tuple with:
      - List of strings with the most specific namespace(s) to use for validation.
      - BuildManager object for opening the file for validation
      - Dict with the full result from NWBHDF5IO.load_namespaces
    """
    from . import NWBHDF5IO  # TODO: modularize to avoid circular import

    catalog = NamespaceCatalog(
        group_spec=NWBGroupSpec, dataset_spec_cls=NWBDatasetSpec, spec_namespace_cls=NWBNamespace
    )
    namespace_dependencies = NWBHDF5IO.load_namespaces(namepsace_catalog=catalog, path=path)

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
        "type": (HDMFIO, type(None)),  # want to do Optional[HDMFIO] but docval complains?
        "doc": "An open IO to an NWB file.",
        "default": None,
    },  # For back-compatability
    {
        "name": "namespace",
        "type": (str, type(None)),  # want to do Optional[str] but docval complains?
        "doc": "A specific namespace to validate against.",
        "default": CORE_NAMESPACE,
    },  # Argument order is for back-compatability
    {
        "name": "paths",
        "type": (list, type(None)),  # want to do Optional[List[str]] but docval complains?
        "doc": "List of NWB file paths.",
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
    returns="Validation errors in the file.",
    rtype=(list, bool),
    is_method=False,
)
def validate(**kwargs):
    """Validate NWB file(s) against a namespace or its cached namespaces."""
    from . import NWBHDF5IO  # TODO: modularize to avoid circular import

    io, paths, use_cached_namespaces, chosen_namespace, verbose = getargs(
        "io", "paths", "use_cached_namespaces", "namespace", "verbose", kwargs
    )
    assert io != paths, "Both 'io' and 'paths' were specified! Please choose only one."

    if io is not None:
        validation_errors = _validate_helper(io=io, namespace=chosen_namespace)
        return validation_errors

    status = 0
    validation_errors = list()
    for path in paths:
        if use_cached_namespaces:
            cached_namespaces, manager, namespace_dependencies = _get_cached_namespaces_to_validate(path=path)

            if any(cached_namespaces):
                namespaces = cached_namespaces
                namespace_message = "cached namespace information"
            else:
                namespace_message = "PyNWB namespace information"
                if verbose:
                    print(
                        f"The file {path} has no cached namespace information. " "Falling back to {namespace_source}.",
                        file=sys.stderr,
                    )
                namespaces = [CORE_NAMESPACE]

        if chosen_namespace:
            if chosen_namespace in namespaces:
                namespaces = [chosen_namespace]
            elif (
                use_cached_namespaces and chosen_namespace in namespace_dependencies
            ):  # validating against a dependency
                for namespace_dependency in namespace_dependencies:
                    if chosen_namespace in namespace_dependencies[namespace_dependency]:
                        status = 1
                        if verbose:
                            print(
                                f"The namespace '{chosen_namespace}' is included by the namespace "
                                "'{namespace_dependency}'. Please validate against that namespace instead.",
                                file=sys.stderr,
                            )
            else:
                status = 1
                if verbose:
                    print(
                        f"The namespace '{chosen_namespace}' could not be found in {namespace_message} as only "
                        f"{namespaces} is present.",
                        file=sys.stderr,
                    )

        with NWBHDF5IO(path, mode="r", manager=manager) as io:
            for namespace in namespaces:
                if verbose:
                    print(f"Validating {path} against {namespace_message} using namespace '{namespace}'.")
                validation_errors += _validate_helper(io=io, namespace=namespace)
    return validation_errors, status


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
    parser.add_argument("paths", type=str, nargs="+", help="NWB file paths")
    parser.add_argument("-n", "--ns", type=str, help="the namespace to validate against")
    feature_parser = parser.add_mutually_exclusive_group(required=False)
    feature_parser.add_argument(
        "--cached-namespace", dest="cached_namespace", action="store_true", help="Use the cached namespace (default)."
    )
    parser.set_defaults(cached_namespace=True)
    args = parser.parse_args()
    status = 0

    if args.list_namespaces:
        for path in args.paths:
            cached_namespaces, _, _, specloc = _get_cached_namespaces_to_validate(path=path)
            print("\n".join(cached_namespaces))
    else:
        validation_errors, validation_status = validate(
            paths=args.paths, use_cached_namespaces=args.cached_namespace, namespace=args.ns, verbose=True
        )
        _print_errors(validation_errors=validation_errors)
        status = status or validation_status or (validation_errors is not None and len(validation_errors) > 0)

    sys.exit(status)


if __name__ == "__main__":  # pragma: no cover
    validate_cli()
