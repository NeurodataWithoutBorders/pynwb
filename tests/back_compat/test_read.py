from pathlib import Path
import warnings

from pynwb import NWBHDF5IO, validate
from pynwb.testing import TestCase


class TestReadOldVersions(TestCase):

    def test_read(self):
        """
        Attempt to read and validate all NWB files in the same folder as this file. The folder should contain NWB files
        from previous versions of NWB. See src/pynwb/testing/make_test_files.py for code to generate the NWB files.
        """
        dir_path = Path(__file__).parent
        nwb_files = dir_path.glob('*.nwb')
        for f in nwb_files:
            with self.subTest(file=f.name):
                with NWBHDF5IO(str(f), 'r') as io:
                    errors = validate(io)
                    io.read()
                    if errors:
                        for e in errors:
                            warnings.warn('%s: %s' % (f.name, e))
                        # TODO uncomment below when validation errors have been fixed
                        # raise Exception('%d validation error(s). See warnings.' % len(errors))
