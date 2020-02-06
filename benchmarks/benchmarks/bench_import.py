from subprocess import call
from sys import executable
from timeit import default_timer

from .common import Benchmark


class Import(Benchmark):
    timer = default_timer

    def execute(self, command):
        call((executable, '-c', command))

    def time_h5py(self):
        # h5py might be taking too long to import on MPI-enabled builds
        # and that would mask pynwb imports,  So let's monitor this import
        # as well
        self.execute('import h5py')

    def time_pynwb(self):
        self.execute('import pynwb')
