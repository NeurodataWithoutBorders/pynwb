# Requires python 3
#
# Reads the stored specification from a freshly created NWB file and exports it
# into pretty printed JSON files.

from datetime import datetime
from dateutil.tz import tzlocal

import os
import io
import json
import sys

import h5py

from pynwb import NWBFile, NWBHDF5IO


def createNWBFile():

    nwbfile = NWBFile('my first synthetic recording',
                      'EXAMPLE_ID',
                      datetime.now(tzlocal()))

    filename = 'specification-extraction.nwb'

    with NWBHDF5IO(filename, 'w') as nwbio:
        nwbio.write(nwbfile, cache_spec=True)

    return filename


def exportSpecification(filename):

    with h5py.File(filename, 'r') as nwb:
        spec = nwb[nwb.attrs['.specloc']]
        for ns in spec.values():
            for version in ns.values():
                for sub in version.values():
                    contents = json.loads(sub[()])

                    def getName(o):
                        return os.path.basename(o.name)

                    filename = "{}_{}_{}_{}.json".format(getName(spec), getName(ns),
                                                         getName(version), getName(sub))
                    with io.open(filename, mode="w", newline="\n") as f:
                        json.dump(contents, fp=f, sort_keys=True,
                                  ensure_ascii=False, separators=(',',':'))


def main(args):

    filename = createNWBFile()
    exportSpecification(filename)
    sys.exit(0)


if __name__ == "__main__":
    main(sys.argv)
