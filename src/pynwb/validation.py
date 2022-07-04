"""Command line tool to Validate an NWB file against a namespace"""
import os
import sys
from argparse import ArgumentParser
from typing import Optional, Tuple, List, Dict

from hdmf.spec import NamespaceCatalog
from hdmf.build import BuildManager
from hdmf.build import TypeMap as TypeMap
from hdmf.utils import docval, getargs
from hdmf.backends.io import HDMFIO
from hdmf.validate import ValidatorMap

from .globals import CORE_NAMESPACE
from .spec import NWBDatasetSpec, NWBGroupSpec, NWBNamespace
from .tools import NWBHDF5IO


def _print_errors(validation_errors):
    if validation_errors:
        print(' - found the following errors:', file=sys.stderr)
        for err in validation_errors:
            print(str(err), file=sys.stderr)
    else:
        print(' - no errors found.')


def _validate_helper(**kwargs):
    errors = validate(**kwargs)
    _print_errors(errors)

    return (errors is not None and len(errors) > 0)


@docval({'name': 'io', 'type': HDMFIO, 'doc': 'the HDMFIO object to read from'},
        {'name': 'namespace', 'type': str, 'doc': 'the namespace to validate against', 'default': CORE_NAMESPACE},
        returns="errors in the file", rtype=list,
        is_method=False)
def validate(**kwargs):
    """Validate the io of an open NWBHDF5IO against a namespace."""
    io, namespace = getargs('io', 'namespace', kwargs)
    builder = io.read_builder()
    validator = ValidatorMap(io.manager.namespace_catalog.get_namespace(name=namespace))
    return validator.validate(builder)


def get_cached_namespaces_to_validate(path: str) -> Tuple[List[str], BuildManager, Dict[str, str]]:
    """
    Determine the most specific namespace(s) (i.e., extensions) that are cached in the given
    NWB file that should be used for validation.
    Example
    -------
    The following example illustrates how we can use this function to validate against namespaces
    cached in a file. This is useful, e.g., when a file was created using an extension
    >>> from pynwb import validate
    >>> from pynwb.validate import get_cached_namespaces_to_validate
    >>> path = "my_nwb_file.nwb"
    >>> validate_namespaces, manager, cached_namespaces = get_cached_namespaces_to_validate(path)
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
    catalog = NamespaceCatalog(NWBGroupSpec, NWBDatasetSpec, NWBNamespace)
    namespace_dependencies = NWBHDF5IO.load_namespaces(catalog, path)

    # determine which namespaces are the most specific (i.e. extensions) and validate against those
    candidate_namespaces = set(namespace_dependencies.keys())
    for namespace_dependency in namespace_dependencies:
        candidate_namespaces -= namespace_dependencies[namespace_dependency].keys()

    # TODO remove this workaround for issue https://github.com/NeurodataWithoutBorders/pynwb/issues/1357
    candidate_namespaces.discard('hdmf-experimental')  # remove validation of hdmf-experimental for now
    namespaces = sorted(candidate_namespaces)

    if len(namespaces) > 0:
        tm = TypeMap(catalog)
        manager = BuildManager(tm)
    else:
        manager = None

    return namespaces, manager, namespace_dependencies


@docval({'name': 'path', 'type': HDMFIO, 'doc': 'the HDMFIO object to read from'},
        {
            'name': 'use_cached_namespaces',
            'type': str, 'doc': 'Whether to use namespaces cached within the file for validation.',
            'default': True
        },
        {
            'name': 'namespace',
            'type': Optional[str], 'doc': 'Whether to use namespaces cached within the file for validation.',
            'default': None
        },
        returns="errors in the file", rtype=list,
        is_method=False)
def validate_file(**kwargs):
    """Validate an NWB file against a namespace or its cached namespaces."""
    path, use_cached_namespaces, namespace = getargs("path", "use_cached_namespaces", "namespace", kwargs)
    
    if use_cached_namespaces:
        catalog = NamespaceCatalog(NWBGroupSpec, NWBDatasetSpec, NWBNamespace)
        ns_deps = NWBHDF5IO.load_namespaces(catalog, path)
        s = set(ns_deps.keys())       # determine which namespaces are the most
        for k in ns_deps:             # specific (i.e. extensions) and validate
            s -= ns_deps[k].keys()    # against those
        # TODO remove this workaround for issue https://github.com/NeurodataWithoutBorders/pynwb/issues/1357
        if 'hdmf-experimental' in s:
            s.remove('hdmf-experimental')  # remove validation of hdmf-experimental for now
        namespaces = list(sorted(s))
        if len(namespaces) > 0:
            tm = TypeMap(catalog)
            manager = BuildManager(tm)
            specloc = "cached namespace information"
        else:
            manager = None
            namespaces = [CORE_NAMESPACE]
            specloc = "pynwb namespace information"
            print("The file {} has no cached namespace information. "
                  "Falling back to {}.".format(path, specloc), file=sys.stderr)

    cached_namespaces, manager, namespace_dependencies = get_cached_namespaces_to_validate(path=path)

    if namespace:
        if namespace in namespaces:
            namespaces = [namespace]
        elif use_cached_namespaces and namespaces in namespace_dependencies:  # validating against a dependency
            for namespace_dependency in namespace_dependencies:
                if namespace in namespace_dependencies[namespace_dependency]:
                    print(
                        f"The namespace '{namespace}' is included by the namespace '{namespace_dependency}'. "
                        "Please validate against that namespace instead.",
                        file=sys.stderr
                    )
            ret = 1
        else:
            print(
                f"The namespace '{namespace}' could not be found in {specloc} as only {namespaces} is present.",
                file=sys.stderr
            )
            ret = 1

    with NWBHDF5IO(path, mode='r', manager=manager) as io:
        for namespace in namespaces:
            print(f"Validating {path} against {specloc} using namespace '{namespace}'.")
            ret = _validate_helper(io=io, namespace=namespace) or ret
    return ret


def validate_cli():  # noqa: C901

    ep = """
    If --ns is not specified, validate against all namespaces in the NWB file.
    """

    parser = ArgumentParser(description="Validate an NWB file", epilog=ep)
    parser.add_argument("paths", type=str, nargs='+', help="NWB file paths")
    # parser.add_argument('-p', '--nspath', type=str, help="the path to the namespace YAML file")
    parser.add_argument("-n", "--ns", type=str, help="the namespace to validate against")
    parser.add_argument("-lns", "--list-namespaces", dest="list_namespaces",
                        action='store_true', help="List the available namespaces and exit.")

    feature_parser = parser.add_mutually_exclusive_group(required=False)
    feature_parser.add_argument("--cached-namespace", dest="cached_namespace", action='store_true',
                                help="Use the cached namespace (default).")
    parser.set_defaults(cached_namespace=True)

    args = parser.parse_args()
    ret = 0

    # TODO Validation against a specific namespace file is currently broken. See pynwb#1396
    # if args.nspath:
    #     if not os.path.isfile(args.nspath):
    #         print("The namespace file {} is not a valid file.".format(args.nspath), file=sys.stderr)
    #         sys.exit(1)
    #
    #     if args.cached_namespace:
    #         print("Turning off validation against cached namespace information "
    #               "as --nspath was passed.", file=sys.stderr)
    #         args.cached_namespace = False

    for path in args.paths:

        if not os.path.isfile(path):
            print(f"The file {path} does not exist.", file=sys.stderr)
            ret = 1
            continue

        cached_namespaces, manager, namespace_dependencies = get_cached_namespaces_to_validate(path=path)
        if args.list_namespaces:
            namespaces = cached_namespaces or [CORE_NAMESPACE]
            print("\n".join(namespaces))
            ret = 0
            continue

        ret = validate_file(path=path, use_cached_namespaces=args.cached_namepsaces, namespace=args.ns)
        if ret == 1:
            continue

    sys.exit(ret)


if __name__ == '__main__':  # pragma: no cover
    validate_cli()
