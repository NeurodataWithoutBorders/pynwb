from argparse import ArgumentParser

from form.backends.hdf5 import HDF5IO
from pynwb import get_build_manager, validate


parser = ArgumentParser(description="Validate an NWB file")
parser.add_argument("path", type=str, help="the path to the NWB file")

args = parser.parse_args()

if not os.exists(args.path):
    print('%s not found' % path, file=sys.stderr)
    sys.exit(1)

errors = validate(HDF5IO(sys.path, get_build_manager()))

if len(errors) > 0:
    for err in errors:
        print('%s - %s' % (err.name, err.reason))
    sys.exit(1)
else:
    print('no errors found')
