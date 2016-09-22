# -*- coding: utf-8 -*-

from .context import sample

import unittest
import h5tools
import h5py
import os



class H5ToolsTest(unittest.TestCase):
    """Tests for h5tools"""

    test_file_path = 'test.h5'

    def setUp(self):
        self.f = h5py.File(test_file_path, 'w')

    def tearDown(self):
        self.f.close()
        os.remove(test_file_path)
        
    def test_iter_fill_divisible_chunks_data_fit(self):
        my_dset = f.require_dataset('test_dataset', shape=(100,), dtype=np.int64, maxshape=(None,))
        h5tools.__iter_fill__(my_dset, 25, range(100))
        assert my_dset[99] == 99

    def test_iter_fill_divisible_chunks_data_nofit(self):
        my_dset = f.require_dataset('test_dataset', shape=(100,), dtype=np.int64, maxshape=(None,))
        h5tools.__iter_fill__(my_dset, 25, range(200))
        assert my_dset[199] == 199

    def test_iter_fill_nondivisible_chunks_data_fit(self):
        my_dset = f.require_dataset('test_dataset', shape=(100,), dtype=np.int64, maxshape=(None,))
        h5tools.__iter_fill__(my_dset, 30, range(100))
        assert my_dset[99] == 99

    def test_iter_fill_nondivisible_chunks_data_nofit(self):
        my_dset = f.require_dataset('test_dataset', shape=(100,), dtype=np.int64, maxshape=(None,))
        h5tools.__iter_fill__(my_dset, 30, range(200))
        assert my_dset[199] == 199


if __name__ == '__main__':
    unittest.main()
