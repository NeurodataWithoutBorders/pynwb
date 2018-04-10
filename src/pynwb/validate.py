from __future__ import print_function

import os
import sys

from argparse import ArgumentParser

from pynwb.form.backends.hdf5 import HDF5IO
from pynwb import validate, load_namespaces, get_manager


def _print_errors(validation_errors):
    if validation_errors:
        print(' - found the following errors:', file=sys.stderr)
        for err in validation_errors:
            print(str(err), file=sys.stderr)
    else:
        print(' - no errors found.')


def main():

    ep = """
    use --nspath to validate against an extension. If --ns is not specified,
    validate against all namespaces in namespace file.
    """

    parser = ArgumentParser(description="Validate an NWB file", epilog=ep)
    parser.add_argument("path", type=str, help="the path to the NWB file")
    parser.add_argument('-p', '--nspath', type=str, help="the path to the namespace file")
    parser.add_argument("-n", "--ns", type=str, help="the namespace to validate against")

    args = parser.parse_args()

    if not os.path.exists(args.path):
        print('%s not found' % args.path, file=sys.stderr)
        sys.exit(1)

    io = HDF5IO(args.path, get_manager())

    if args.nspath is not None:
        namespaces = load_namespaces(args.nspath)
        if args.ns is not None:
            print('Validating against %s from %s.' % (args.ns, args.ns_path))
        else:
            print('Validating using namespaces in %s.' % args.nspath)
            for ns in namespaces:
                print('Validating against %s' % ns)
                errors = validate(io, ns)
                _print_errors(errors)
    else:
        errors = validate(io)
        print('Validating against core namespace')
        _print_errors(errors)


if __name__ == '__main__':  # pragma: no cover
    main()
