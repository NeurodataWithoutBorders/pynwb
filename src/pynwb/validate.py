import os
import sys
from argparse import ArgumentParser

from hdmf.spec import NamespaceCatalog
from hdmf.build import BuildManager
from hdmf.build import TypeMap as TypeMap

from pynwb import validate, CORE_NAMESPACE, NWBHDF5IO
from pynwb.spec import NWBDatasetSpec, NWBGroupSpec, NWBNamespace

def _print_results(results, txt):

    if results:
        print(' - found the following {}:'.format(txt), file=sys.stderr)
        for x in results:
            print(str(x), file=sys.stderr)
    else:
        print(" - no {} found.".format(txt))


def _validate_helper(**kwargs):
    severity = kwargs.pop('severity')

    issues = validate(**kwargs)

    errors = list(filter(lambda issue: issue.severity >= severity, issues))
    warnings = list(filter(lambda issue: issue.severity < severity, issues))

    _print_results(errors, "errors")
    _print_results(warnings, "warnings")

    return errors is not None and len(errors) > 0


def main():

    ep = """
    use --nspath to validate against an extension. If --ns is not specified,
    validate against all namespaces in namespace file.
    """

    parser = ArgumentParser(description="Validate an NWB file", epilog=ep)
    parser.add_argument("paths", type=str, nargs='+', help="NWB file paths")
    parser.add_argument('-p', '--nspath', type=str, help="the path to the namespace YAML file")
    parser.add_argument("-n", "--ns", type=str, help="the namespace to validate against")
    parser.add_argument("-lns", "--list-namespaces", dest="list_namespaces",
                        action='store_true', help="List the available namespaces and exit.")

    feature_parser = parser.add_mutually_exclusive_group(required=False)
    feature_parser.add_argument("--cached-namespace", dest="cached_namespace", action='store_true',
            help="Use the cached namespace (default: %(default)s).", default=True)
    feature_parser.add_argument('--no-cached-namespace', dest="cached_namespace", action='store_false',
                                help="Don't use the cached namespace.")
    feature_parser.add_argument('--severity', dest="severity", type=int,
                                help="Report anything with the given severity or higher as error (default: %(default)s).",
                                default=10, choices=range(0, 11))

    args = parser.parse_args()
    ret = 0

    if args.nspath:
        if not os.path.isfile(args.nspath):
            print("The namespace file {} is not a valid file.".format(args.nspath), file=sys.stderr)
            sys.exit(1)

        if args.cached_namespace:
            print("Turning off validation against cached namespace information "
                  "as --nspath was passed.", file=sys.stderr)
            args.cached_namespace = False

    for path in args.paths:

        if not os.path.isfile(path):
            print("The file {} does not exist.".format(path), file=sys.stderr)
            ret = 1
            continue

        if args.cached_namespace:
            catalog = NamespaceCatalog(NWBGroupSpec, NWBDatasetSpec, NWBNamespace)
            ns_deps = NWBHDF5IO.load_namespaces(catalog, path)
            s = set(ns_deps.keys())       # determine which namespaces are the most
            for k in ns_deps:             # specific (i.e. extensions) and validate
                s -= ns_deps[k].keys()    # against those
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
            namespaces = [CORE_NAMESPACE]
            specloc = "pynwb namespace information"

        if args.list_namespaces:
            print("\n".join(namespaces))
            ret = 0
            continue

        if args.ns:
            if args.ns in namespaces:
                namespaces = [args.ns]
            else:
                print("The namespace {} could not be found in {} as only {} is present.".format(
                      args.ns, specloc, namespaces), file=sys.stderr)
                ret = 1
                continue

        with NWBHDF5IO(path, mode='r', manager=manager) as io:
            for ns in namespaces:
                print("Validating {} against {} using namespace {}.".format(path, specloc, ns))
                ret = ret or _validate_helper(io=io, namespace=ns, severity=args.severity)

    sys.exit(ret)


if __name__ == '__main__':  # pragma: no cover
    main()
