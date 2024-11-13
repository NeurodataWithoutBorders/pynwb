"""Command line tool to Validate an NWB file against a namespace."""
import json
import sys
from argparse import ArgumentParser
from pathlib import Path

from pynwb.validation import validate, get_cached_namespaces_to_validate


def _print_errors(validation_errors: list):
    if validation_errors:
        print(" - found the following errors:", file=sys.stderr)
        for err in validation_errors:
            print(str(err), file=sys.stderr)
    else:
        print(" - no errors found.")


def validation_cli():
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
            status = int(validation_errors is not None and len(validation_errors) > 0)
        except ValueError as e:
            print(e, file=sys.stderr)
            status = 1
        
    # write output to json file
    if args.json_file_path is not None:
        with open(args.json_file_path, "w") as f:
            json_report = {'exitcode': status, 'errors': [str(e) for e in validation_errors]}
            json.dump(obj=json_report, fp=f)
            print(f"Report saved to {str(Path(args.json_file_path).absolute())}!")

    sys.exit(status)


if __name__ == "__main__":  # pragma: no cover
    validation_cli()
