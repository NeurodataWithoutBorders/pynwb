"""
This script adds an 'object_id' attribute to each neurodata_type of an hdf5 file that was written before object IDs
existed. Specifically, it traverses through the hierarchy of objects in the file and sets the 'object_id' attribute
to a UUID4 string on each group, dataset, and link that has a 'neurodata_type' attribute and does not have an
'object_id' attribute.

Usage: python add_object_id filename
"""


from h5py import File
from uuid import uuid4
import sys


def add_uuid(name, obj):
    if 'neurodata_type' in obj.attrs and 'object_id' not in obj.attrs:
        obj.attrs['object_id'] = str(uuid4())
        print('Adding uuid4 %s to %s' % (obj.attrs['object_id'], str(obj)))


def main():
    filename = sys.argv[1]
    with File(filename, 'a') as f:
        f.visititems(add_uuid)


if __name__ == '__main__':
    main()
