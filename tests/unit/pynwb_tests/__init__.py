import os
from datetime import datetime

from pynwb import NWBFile, NWBHDF5IO


class ContainerRoundTrip:
    def __init__(self, container, filename='temp.nwb'):
        self.container = container
        self.filename = filename

    def __enter__(self):
        nwbfile = NWBFile(source='source',
                          session_description='session_description',
                          identifier='identifier',
                          session_start_time=datetime.now(),
                          file_create_date=datetime.now(),
                          institution='institution',
                          lab='lab')
        module = nwbfile.create_processing_module('test',
                                                  source='source',
                                                  description='description')
        module.add_container(self.container)

        with NWBHDF5IO(self.filename, 'w') as io:
            io.write(nwbfile)
        self.io = NWBHDF5IO(self.filename, 'r')
        nwbfile = self.io.read()
        container = nwbfile.modules['test'].containers[0]
        return container

    def __exit__(self, type, value, traceback):
        self.io.close()
        os.remove(self.filename)


class NWBFileRoundTrip:
    def __init__(self, nwbfile, filename='temp.nwb'):
        self.nwbfile = nwbfile
        self.filename = filename

    def __enter__(self):

        with NWBHDF5IO(self.filename, 'w') as io:
            io.write(self.nwbfile)
        self.io = NWBHDF5IO(self.filename, 'r')
        return self.io.read()

    def __exit__(self, type, value, traceback):
        self.io.close()
        os.remove(self.filename)


class MockNWBFile(NWBFile):
    def __init__(self):
        super().__init__(source='source',
                         session_description='session_description',
                         identifier='identifier',
                         session_start_time=datetime.now(),
                         file_create_date=datetime.now(),
                         institution='institution',
                         lab='lab')
