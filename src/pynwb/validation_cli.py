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
    """CLI wrapper around pynwb.validate.
    
    Note: this CLI wrapper checks for compliance with the NWB schema. 
    It is recommended to use the NWBInspector CLI for more comprehensive validation of both
    compliance with the schema and compliance of data with NWB best practices.
    """
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
    parser.add_argument("--json-output-path", dest="json_output_path", type=str, 
                        help="Write json output to this location.")
    feature_parser = parser.add_mutually_exclusive_group(required=False)
    feature_parser.add_argument(
        "--no-cached-namespace",
        dest="no_cached_namespace",
        action="store_true",
        help="Use the namespaces installed by PyNWB (true) or use the cached namespaces (false; default).",
    )
    parser.set_defaults(no_cached_namespace=False)
    args = parser.parse_args()

    status = 0
    for path in args.paths:
        if args.list_namespaces:
            cached_namespaces, _, _ = get_cached_namespaces_to_validate(path=path)
            print("\n".join(cached_namespaces))
        else:
            validation_errors = []
            try:
                val_errors = validate(
                    path=path, use_cached_namespaces=not args.no_cached_namespace, namespace=args.ns, verbose=True, 
                )
                _print_errors(validation_errors=val_errors)
                status = status or int(val_errors is not None and len(val_errors) > 0)
                validation_errors.append(val_errors)
            except ValueError as e:
                print(e, file=sys.stderr)
                status = 1
        
    # write output to json file
    if args.json_output_path is not None:
        with open(args.json_output_path, "w") as f:
            json_report = {'exitcode': status, 'errors': [str(e) for e in validation_errors]}
            json.dump(obj=json_report, fp=f)
            print(f"Report saved to {str(Path(args.json_output_path).absolute())}!")

    sys.exit(status)


if __name__ == "__main__":  # pragma: no cover
    validation_cli()
