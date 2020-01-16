import os
import sys
from argparse import ArgumentParser

from hdmf.spec import NamespaceCatalog
from hdmf.build import BuildManager
from hdmf.build import TypeMap as TypeMap
from hdmf.backends.hdf5 import HDF5IO

from pynwb import validate, available_namespaces, NWBHDF5IO
from pynwb.spec import NWBDatasetSpec, NWBGroupSpec, NWBNamespace


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


def main():

    ep = """
    use --nspath to validate against an extension. If --ns is not specified,
    validate against all namespaces in namespace file.
    """

    parser = ArgumentParser(description="Validate an NWB file", epilog=ep)
    parser.add_argument("paths", type=str, nargs='+', help="NWB file paths")
    parser.add_argument('-p', '--nspath', type=str, help="the path to the namespace YAML file")
    parser.add_argument("-n", "--ns", type=str, help="the namespace to validate against")

    feature_parser = parser.add_mutually_exclusive_group(required=False)
    feature_parser.add_argument("--cached-namespace", dest="cached_namespace", action='store_true',
                                help="Use the cached namespace (default).")
    feature_parser.add_argument('--no-cached-namespace', dest="cached_namespace", action='store_false',
                                help="Don't use the cached namespace.")
    parser.set_defaults(cached_namespace=True)

    args = parser.parse_args()
    ret = 0

    if args.nspath:
        if not os.path.isfile(args.nspath):
            print("The namespace file {} is not a valid file.".format(args.nspath), file=sys.stderr)
            sys.exit(1)

        if args.cached_namespace:
            print("Turning off validation against cached namespace information"
                  "as --nspath was passed.", file=sys.stderr)
            args.cached_namespace = False

    for path in args.paths:

        if not os.path.isfile(path):
            print("The file {} does not exist.".format(path), file=sys.stderr)
            ret = 1
            continue

        if args.cached_namespace:
            catalog = NamespaceCatalog(NWBGroupSpec, NWBDatasetSpec, NWBNamespace)
            namespaces = HDF5IO.load_namespaces(catalog, path).keys()
            if len(namespaces) > 0:
                tm = TypeMap(catalog)
                manager = BuildManager(tm)
                specloc = "cached namespace information"
            else:
                manager = None
                namespaces = available_namespaces()
                specloc = "pynwb namespace information"
                print("The file {} has no cached namespace information. "
                      "Falling back to {}.".format(path, specloc), file=sys.stderr)
        elif args.nspath:
            catalog = NamespaceCatalog(NWBGroupSpec, NWBDatasetSpec, NWBNamespace)
            namespaces = catalog.load_namespaces(args.nspath)

            if len(namespaces) == 0:
                print("Could not load namespaces from file {}.".format(args.nspath), file=sys.stderr)
                sys.exit(1)

            tm = TypeMap(catalog)
            manager = BuildManager(tm)
            specloc = "--nspath namespace information"
        else:
            manager = None
            namespaces = available_namespaces()
            specloc = "pynwb namespace information"

        if args.ns:
            if args.ns in namespaces:
                namespaces = [args.ns]
            else:
                print("The namespace {} could not be found in {}.".format(args.ns, specloc), file=sys.stderr)
                ret = 1
                continue

        with NWBHDF5IO(path, mode='r', manager=manager) as io:
            for ns in namespaces:
                print("Validating {} against {} using namespace {}.".format(path, specloc, ns))
                ret = ret or _validate_helper(io=io, namespace=ns)

    sys.exit(ret)


if __name__ == '__main__':  # pragma: no cover
    main()
