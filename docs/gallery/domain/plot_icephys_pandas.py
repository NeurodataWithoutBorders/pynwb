# -*- coding: utf-8 -*-
'''
.. _icephys_pandas_tutorial:

Query intracellular electrophysiology metadata
==============================================

This tutorial focuses on using Pandas to query experiment metadata for
intracellular electrophysiology experiments using the metadata tables
from the :py:meth:`~pynwb.icephys` module. See the :ref:`icephys_tutorial_new`
tutorial for an introduction to the intracellular electrophysiology metadata
tables and how to create an NWBFile for intracellular electrophysiology data.
'''

#######################
# Imports used in the tutorial
# ------------------------------

# sphinx_gallery_thumbnail_path = 'figures/gallery_thumbnails_icephys_pandas.png'
# Standard Python imports
from datetime import datetime
from dateutil.tz import tzlocal
import numpy as np
import pandas
# Set Pandas rendering option to avoid very wide cells
pandas.set_option("display.max_colwidth", 30)
pandas.set_option("display.max_rows", 10)
pandas.set_option("display.max_columns", 6)

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
# Converting ICEphys metadata tables to Pandas DataFrames
# -------------------------------------------------------
#

#######################
# Using nested DataFrames
# ^^^^^^^^^^^^^^^^^^^^^^^
# Using the :py:meth:`~hdmf.common.table.DynamicTable.to_dataframe` method we can easily convert tables
# to Pandas  `DataFrame <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html>`_.

exp_cond_df = root_table.to_dataframe()
exp_cond_df

#######################
# By default, the method will resolve :py:class:`~hdmf.common.table.DynamicTableRegion`
# references and include the rows that are referenced in related tables as  `DataFrame`_
# objects, resulting in a hierarchically nested `DataFrame`_. For example, looking at a single cell of the
# ``repetitions`` column of our :py:class:`~pynwb.icephys.ExperimentalConditionsTable` table
# we get the corresponding subset of repetitions from the  py:class:`~pynwb.icephys.RepetitionsTable`.

exp_cond_df.iloc[0]['repetitions']


#######################
# Using indexed DataFrames
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#
# Depending on the particular analysis we may be interested only in a particular table and do not
# want to recursively load and resolve all the linked tables. By setting ``index=True`` when
# converting the table :py:meth:`~hdmf.common.table.DynamicTable.to_dataframe` the
# :py:class:`~hdmf.common.table.DynamicTableRegion` links will be represented as
# lists of integers indicating the rows in the target table (without loading data from
# the referenced table).

root_table.to_dataframe(index=True)

#######################
# To resolve links related to a set of rows, we can then simply use the corresponding
# :py:class:`~hdmf.common.table.DynamicTableRegion` column from our original table, e.g:

root_table['repetitions'][0]  # Look-up the repetitions for the first experimental condition


#######################
# We can naturally also resolve links ourselves by looking up the relevant table and
# then accessing elements of the table directly

# All DynamicTableRegion columns in the ICEphys table are indexed so we first need to
# follow the ".target" to the VectorData and then look up the table via ".table"
target_table = root_table['repetitions'].target.table
target_table[[0,1]]


#######################
# .. note:: We can also explicitly exclude the :py:class:`~hdmf.common.table.DynamicTableRegion` columns
#    (or any other column) from the `DataFrame`_ using e.g., ``root_table.to_dataframe(exclude={'repetitions', })``.


#######################
# Converting linked tables to a single, hierarchical DataFrame
# """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# To gain a more direct overview of all metadata at once and avoid iterating across levels of nested
# DataFrames during analysis, it can be useful to flatten (or unnest) nested DataFrames, expanding the
# nested DataFrames by adding their columns to the main table and expanding the corresponding rows in
# parent table by duplicating the data from the existing columns across the new rows.
# For example, an experimental condition represented by a single row in the
# :py:class:`~pynwb.icephys.ExperimentalConditionsTable` containing 5 repetitions would be expanded
# to 5 rows, each containing a copy of the metadata from the experimental condition along with the
# metadata of one of the repetitions. Repeating this process recursively, a single row in the
# :py:class:`~pynwb.icephys.ExperimentalConditionsTable` will then ultimatly expand to the total
# number of intracellular recordings from the :py:class:`~pynwb.icephys.IntracellularRecordingsTable`
# that belong to the experimental conditions table.
#
# HDMF povides a several convenience functions to help with this process. Using the
# :py:func:`~hdmf.common.hierarchicaltable.to_hierarchical_dataframe` method we can transform
# our hierarchical table into a single Pandas `DataFrame`_.
# To avoid duplication of data in the display, the hierarchy is represented as a Pandas
# `MultiIndex <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.MultiIndex.html>`_ on
# the rows so that only the data from the last table in our hierarchy (i.e. here the
# :py:class:`~pynwb.icephys.IntracellularRecordingsTable`) is represented as columns.


from hdmf.common.hierarchicaltable import to_hierarchical_dataframe
icephys_meta_df = to_hierarchical_dataframe(root_table)

#######################
#

# Print table as text too avoid too wide display in ReadTheDocs
print(icephys_meta_df.to_string())



#######################
# Depending on the analysis, it can be useful to further process our `DataFrame`_. Using the standard
# `reset_index <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.reset_index.html>`_
# function we can turn the data from the `MultiIndex`_ to columns sof the  table itself,
# effectively denormalizing the display by repeating all data across rows. HDMF then also
# provides: 1) :py:func:`~hdmf.common.hierarchicaltable.drop_id_columns` to remove all "id" columns
# and 2) :py:func:`~hdmf.common.hierarchicaltable.flatten_column_index` to turn the
# `MultiIndex`_
# on the columns of our table into a regular
# `MultiIndex`_ of tuples.
#

from hdmf.common.hierarchicaltable import drop_id_columns, flatten_column_index
# Reset the index of the dataframe and turn the values into columns instead
icephys_meta_df.reset_index(inplace=True)
# Flatten the column-index, turning the pandas.MultiIndex into a regular pandas.Index of tuples
flatten_column_index(icephys_meta_df, max_levels=2, inplace=True)
# Remove the id columns
drop_id_columns(icephys_meta_df, inplace=True)
# Display the DataFrame in the html docs
icephys_meta_df



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
# * Given a stimulus type, get all the repetitions in which it is present
# * Given a stimulus type and a repetition, get all the responses
# * Given a stimulus or response, return all other stimuli and responses recorded during the same sweep*
# * Given a sweep, return its repetition
# * Given a repetition, return all sweeps within that repetition
# * Given a sweep or repetition, return its condition
# * Given a condition, return all sweeps or repetitions
# * Given a sweep, return all other sweeps of the same repetition
# * Given a stimulus and a condition, return all sweeps across repetitions and average the responses
#
# In general we can perform these queries in two main ways:
#
# 1. Use the individual :py:class:`~hdmf.common.table.DynamicTables` directly, leaving the data on
#    disk until it is needed
# 2. Load all metadata into a `DataFrame`_ and perform queries on the tables in memory.
#


