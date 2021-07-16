# -*- coding: utf-8 -*-
'''
.. _icephys_pandas_tutorial:

Query intracellular electrophysiology experiment metadata
=========================================================

This tutorial focuses on using Pandas to query experiment metadata for
intracellular electrophysiology experiments using the metadata tables
from the :py:meth:`~pynwb.icephys` module. See the :ref:`icephys_tutorial_new`
tutorial for an introduction to the intracellular electrophysiology metadata
tables and how to create an NWBFile for intracellular electrophysiology data.
'''

#######################
# Imports used in the tutorial
# ------------------------------

# sphinx_gallery_thumbnail_path = 'figures/gallery_thumbnails_icephys.png'
# Standard Python imports
from datetime import datetime
from dateutil.tz import tzlocal
import numpy as np
import pandas
pandas.set_option("display.max_colwidth", 30)  # Set Pandas rendering option to avoid very wide cells

# Import main NWB file class
from pynwb import NWBFile
# Import icephys TimeSeries types used
from pynwb.icephys import VoltageClampStimulusSeries, VoltageClampSeries
# Import I/O class used for reading and writing NWB files
from pynwb import NWBHDF5IO
# Import additional core datatypes used in the example
from pynwb.core import DynamicTable, VectorData

#######################
# Example setup
# ---------------
#
# Generate a simple example NWBFile with dummy intracellular electrophysiology data.

from pynwb.testing.icephys_testutils  import create_icephys_testfile
test_filename = "icephys_pandas_testfile.nwb"
nwbfile = create_icephys_testfile(
     filename=test_filename,    # write the file to disk for testing
     add_custom_columns=True,   # Add a custom column to each icephys metadata table for testing
     randomize_data=True        # Randomize the data in the simulus and response for some more realistic behavior
    )


#######################
# Get the parent metadata table
# -----------------------------
#
# The intracellular electrophysiology metadata consists of a hierarchy of DynamicTables, i.e.,
# :py:class:`~pynwb.icephys.ExperimentalConditionsTable` -->
# :py:class:`~pynwb.icephys.RepetitionsTable` -->
# :py:class:`~pynwb.icephys.SequentialRecordingsTable` -->
# :py:class:`~pynwb.icephys.SimultaneousRecordingsTable` -->
# :py:class:`~pynwb.icephys.IntracellularRecordingsTable`.
# However, in a given :py:class:`~pynwb.file.NWBFile` not all tables may exist, but a user may choose
# to exclude tables from the top of the hierarchy. To locate the table that defines the root of the
# table hierarchy, we can simply use the convenience function
# :py:meth:`~pynwb.file.NWBFile.get_icephys_meta_parent_table`. Since our file contains all tables,
# the root in this case is the same as :py:meth:`~pynwb.file.NWBFile.icephys_experimental_conditions`.

root_table =  nwbfile.get_icephys_meta_parent_table()

#######################
# Inspecting the table hierarchy
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# For any given tablem we can further check if and which columns are foreign
# :py:class:`~hdmf.common.table.DynamicTableRegion` columns pointing to other tables
# via the the :py:meth:`~hdmf.common.table.DynamicTable.has_foreign_columns` and
# :py:meth:`~hdmf.common.table.DynamicTable.get_foreign_columns`, respectively.
#

print("Has Foreign Columns:", root_table.has_foreign_columns())
print("Foreign Columns:", root_table.get_foreign_columns())

#######################
# Using :py:meth:`~hdmf.common.table.DynamicTable.get_linked_tables` we can then also
# look at all links defined directly or indirectly from a given table to other tables.
# The result is a list of dicts containing for each found link the:
#
# * *"source_table"* :py:class:`~hdmf.common.table.DynamicTable` object
# * *"source_column"* :py:class:`~hdmf.common.table.DynamicTableRegion` column from the source table,
# * *"target_table"* :py:class:`~hdmf.common.table.DynamicTable`  (which is the same as *source_column.table*).

linked_tables = root_table.get_linked_tables()

# Print the links
for t in linked_tables:
    print("(%s, %s) ----> %s" %
          (t['source_table'].name, t['source_column'].name, t['target_table'].name))

#######################
# Converting tables to Pandas DataFrames
# --------------------------------------
#

#######################
# Convert linked tables to nested DataFrames
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# Using the :py:meth:`~hdmf.common.table.DynamicTable.to_dataframe` method we can easily convert tables
# to Pandas DataFrames.

exp_cond_df = root_table.to_dataframe()
exp_cond_df

#######################
# By default, the method will resolve :py:class:`~hdmf.common.table.DynamicTableRegion`
# references and include the rows that are referenced in related tables as DataFrame objects,
# resulting in a hierarchically nested dataframe. For example, looking at a single cell of the
# ``repetitions`` column of our :py:class:`~pynwb.icephys.ExperimentalConditionsTable` table
# we get the corresponding subset of repetitions from our py:class:`~pynwb.icephys.RepetitionsTable
# that correspond to th given row, e.g.:

exp_cond_df.iloc[0]['repetitions']

#######################
# Storing data in hierarchical tables has the advantage that it allows us to avoid duplication of
# metadata. E.g., for a single experiment we only need to describe the metadata that is constant
# across an experimental condition as a single row in the :py:class:`~pynwb.icephys.ExperimentalConditionsTable`
# without having to replicate the same information across all repetitions and sequential-, simultaneous-, and
# individual intracellular recordings. For analysis, this means that we can easily focus on individual
# aspects of an experiment while still being able to easily access information about information from
# related tables.

#######################
# Flattening and nested DataFrames
# """"""""""""""""""""""""""""""""
# To gain a more direct overview of all metadata at once and avoid iterating across levels of nested
# DataFrames, it can be useful to flatten (or unnest) nested DataFrames, expanding nested DataFrames to
# rows in a table while duplicating the data stored in the corresponding parent rows. For example, an
# experimental condition represented by a single row in the
# py:class:`~pynwb.icephys.ExperimentalConditionsTable` containing 5 repetitions would be expanded
# to 5 rows, each containing a copy of the metadata from the experimental contidtion along with the
# metadata of one of the repetitions. Repeating this process recursively, a single row in the
# py:class:`~pynwb.icephys.ExperimentalConditionsTable` will then utlimatly expand to the total
# number of intracellular recordings from the :py:class:`~pynwb.icephys.IntracellularRecordingsTable`
# that belong to the experimental condition.

from hdmf.common.hierarchicaltable import denormalize_nested_dataframe
denormalize_nested_dataframe(exp_cond_df)

#######################
# Convert a single level to DataFrame
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#
# Depending on the particular analysis we may be interested only in a particular table and do not
# want to recursively load and resolve all the linked tables. We can do this simply by setting
# ``index=True`` when converting the table. In this case :py:class:`~hdmf.common.table.DynamicTableRegion`
# links will be simply converted to the corresponding list of integers indicating the rows in the
# target table (without loading data from the referenced table).

root_table.to_dataframe(index=True)

#######################
# We can also explicitly exclude columns from the conversion to a dataframe by providing a ``set``
# of strings with the names of the columns to the ``exclude`` parameter.

root_table.to_dataframe(exclude={'repetitions', })


#######################
# Performing common metadata queries
# ----------------------------------
#
# Here some common queries we identified
#
# * Given a response, return the stimulus
# * Given a stimulus, return the response
# * Given a stimulus, return the stimulus type
# * Given an electrode, return all sweeps recorded with it
# * Given a stimulus type, return all derived stimuli
# * Get the list of all stimulus types
# * Given a stimulus type, get all the repetitions in which it is present [Enrico]
# * Given a stimulus type and a repetition, get all the responses [Enrico]
# * Given a stimulus or response, return all other stimuli and responses recorded during the same sweep*
# * Given a sweep, return its repetition
# * Given a repetition, return all sweeps within that repetition
# * Given a sweep or repetition, return its condition
# * Given a condition, return all sweeps or repetitions
# * Given a sweep, return all other sweeps of the same repetition
# * Given a stimulus and a condition, return all sweeps across repetitions and average the responses
#
# In general we can perfom these queries in two main ways:
#
# 1. Use the individual :py:class:`~hdmf.common.table.DynamicTables` directly, leaving the data on disk until it is needed
# 2. Load all metadata as nested (or flat) Pandas DataFrame and perform queries on the pandas tables.
#
# Below we will illustrate both approaches for a select set of the queries listed above.
#

