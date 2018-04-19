"""
Iterative Data Write
====================

This example demonstrate how to iteratively write data arrays with applications to
writing large arrays without loading all data into memory and streaming data write.

"""

####################
#
# ------------
#

from pynwb.form.data_utils import DataChunkIterator
from pynwb.form.data_utils import DataChunk

