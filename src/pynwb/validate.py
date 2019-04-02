from __future__ import print_function

import os
import sys

from argparse import ArgumentParser

from pynwb import validate, load_namespaces, get_manager, NWBHDF5IO


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

    return (errors and len(errors) > 0)


def main():

    ep = """
    use --nspath to validate against an extension. If --ns is not specified,
    validate against all namespaces in namespace file.
    """

    parser = ArgumentParser(description="Validate an NWB file", epilog=ep)
    parser.add_argument("paths", type=str, nargs='+', help="NWB file paths")
    parser.add_argument('-p', '--nspath', type=str, help="the path to the namespace file")
    parser.add_argument("-n", "--ns", type=str, help="the namespace to validate against")

    args = parser.parse_args()
    ret = 0

    for path in args.paths:

        if not os.path.exists(path):
            print('%s not found' % path, file=sys.stderr)
            ret = 1
            continue

        with NWBHDF5IO(path, get_manager(), mode='r') as io:

            if args.nspath is not None:
                namespaces = load_namespaces(args.nspath)
                if args.ns is not None:
                    print('Validating %s against %s from %s.' % (path, args.ns, args.ns_path))
                    ret = ret or _validate_helper(io=io, namespace=args.ns)
                else:
                    print('Validating %s using namespaces in %s.' % (path, args.nspath))
                    for ns in namespaces:
                        print('Validating against %s' % ns)
                        ret = ret or _validate_helper(io=io, namespace=ns)
            else:
                print('Validating %s against core namespace' % path)
                ret = ret or _validate_helper(io=io)

    sys.exit(ret)


if __name__ == '__main__':  # pragma: no cover
    main()
