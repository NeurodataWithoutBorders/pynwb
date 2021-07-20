# -*- coding: utf-8 -*-
'''
.. _icephys_pandas_tutorial:

Query intracellular electrophysiology metadata
==============================================

This tutorial focuses on using pandas to query experiment metadata for
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
import numpy as np
import pandas
# Set pandas rendering option to avoid very wide tables in the html docs
pandas.set_option("display.max_colwidth", 30)
pandas.set_option("display.max_rows", 10)
pandas.set_option("display.max_columns", 6)

#######################
# Example setup
# ---------------
#
# Generate a simple example NWBFile with dummy intracellular electrophysiology data.

from pynwb.testing.icephys_testutils import create_icephys_testfile
test_filename = "icephys_pandas_testfile.nwb"
nwbfile = create_icephys_testfile(
     filename=test_filename,     # write the file to disk for testing
     add_custom_columns=True,    # Add a custom column to each icephys metadata table for testing
     randomize_data=True,        # Randomize the data in the simulus and response for some more realistic behavior
     with_missing_stimulus=True  # Don't include the stimulus for row 0 and 10 so we can illustrate this case
    )


#######################
# Accessing the ICEphys metadata tables
# -------------------------------------
#
# Get the parent metadata table
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#
# The intracellular electrophysiology metadata consists of a hierarchy of DynamicTables, i.e.,
# :py:class:`~pynwb.icephys.ExperimentalConditionsTable` -->
# :py:class:`~pynwb.icephys.RepetitionsTable` -->
# :py:class:`~pynwb.icephys.SequentialRecordingsTable` -->
# :py:class:`~pynwb.icephys.SimultaneousRecordingsTable` -->
# :py:class:`~pynwb.icephys.IntracellularRecordingsTable`.
# However, in a given :py:class:`~pynwb.file.NWBFile` not all tables may exist, but a user may choose
# to exclude tables from the top of the hierarchy (e.g.,, a file may only contain
# :py:class:`~pynwb.icephys.SimultaneousRecordingsTable` and  :py:class:`~pynwb.icephys.IntracellularRecordingsTable`
# while omitting all of the other table that are higher in the hierarchy).
# To provide a consistent interface for users, PyNWB allows us to easily locate the table
# that defines the root of the table hierarchy via the function
# :py:meth:`~pynwb.file.NWBFile.get_icephys_meta_parent_table`.

root_table = nwbfile.get_icephys_meta_parent_table()
print(root_table.neurodata_type)

#######################
# Getting a specific ICEphys metadata table
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#
# We can retrieve any of the ICEphys metadata tables via the corresponding properties of NWBFile, i.e.,
# :py:meth:`~pynwb.file.NWBFile.intracellular_recordings`,
# :py:meth:`~pynwb.file.NWBFile.icephys_simultaneous_recordings`,
# :py:meth:`~pynwb.file.NWBFile.icephys_sequential_recordings`,
# :py:meth:`~pynwb.file.NWBFile.icephys_sequential_recordings`,
# :py:meth:`~pynwb.file.NWBFile.icephys_repetitions`,
# :py:meth:`~pynwb.file.NWBFile.icephys_experimental_conditions`.
# The property will be ``None`` in case the file does not contain the corresponding table.
# As such we can also easily check if a NWBFile contains a particular ICEphys metadata table via, e.g.:

nwbfile.icephys_sequential_recordings is not None


#######################
#
# .. warning:: Always use the :py:class:`~pynwb.file.NWBFile` properties rather than the
#              corresponding get methods if you only want to retrieve the ICEphys metadata tables.
#              The get methods (e.g., :py:meth:`~pynwb.file.NWBFile.get_icephys_simultaneous_recordings`)
#              are designed to always return a corresponding ICEphys metadata table for the file and will
#              automatically add the missing table (and all required tables that are  lower in the hierarchy)
#              to the file. This behavior is to ease populating the ICEphys metadata tables when creating
#              or updating an :py:class:`~pynwb.file.NWBFile`.
#


#######################
# Inspecting the table hierarchy
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# For any given table we can further check if and which columns are foreign
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
for i, t in enumerate(linked_tables):
    print("%s (%s, %s) ----> %s" %
          ("    " * i, t['source_table'].name, t['source_column'].name, t['target_table'].name))

#######################
# Converting ICEphys metadata tables to pandas DataFrames
# -------------------------------------------------------
#

#######################
# Using nested DataFrames
# ^^^^^^^^^^^^^^^^^^^^^^^
# Using the :py:meth:`~hdmf.common.table.DynamicTable.to_dataframe` method we can easily convert tables
# to pandas  `DataFrame <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html>`_.

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
# In contrast to the other ICEphys metadata tables the
# :py:class:`~pynwb.icephys.IntracellularRecordingsTable` does not contain any
# :py:class:`~hdmf.common.table.DynamicTableRegion` columns but as an
# :py:class:`~hdmf.common.alignedtable.AlignedDynamicTable` contains sub-tables for
# ``electrodes``, ``stimuli``, and ``responses``. For convenience the
# :py:meth:`~pynwb.icephys.IntracellularRecordingsTable.to_dataframe` of the
# :py:class:`~pynwb.icephys.IntracellularRecordingsTable` provides a few
# additonal optional parameters to optionally ignore the ids of the category tables
# (via ``ignore_category_ids=True``) or to convert the electrode, stimulus, and
# response references to ObjectIds. For example:
#

nwbfile.intracellular_recordings.to_dataframe(ignore_category_ids=True,
                                              electrode_refs_as_objectids=True,
                                              stimulus_refs_as_objectids=True,
                                              response_refs_as_objectids=True)


#######################
# Using indexed DataFrames
# ^^^^^^^^^^^^^^^^^^^^^^^^
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
target_table[[0, 1]]


#######################
# .. note:: We can also explicitly exclude the :py:class:`~hdmf.common.table.DynamicTableRegion` columns
#    (or any other column) from the `DataFrame`_ using e.g., ``root_table.to_dataframe(exclude={'repetitions', })``.


#######################
# Using a single, hierarchical DataFrame
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
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
# our hierarchical table into a single pandas `DataFrame`_.
# To avoid duplication of data in the display, the hierarchy is represented as a pandas
# `MultiIndex <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.MultiIndex.html>`_ on
# the rows so that only the data from the last table in our hierarchy (i.e. here the
# :py:class:`~pynwb.icephys.IntracellularRecordingsTable`) is represented as columns.


from hdmf.common.hierarchicaltable import to_hierarchical_dataframe
icephys_meta_df = to_hierarchical_dataframe(root_table)

#######################
#

# Print table as text to avoid too wide display in HTML docs
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
flatten_column_index(dataframe=icephys_meta_df, max_levels=2, inplace=True)
# Remove the id columns
drop_id_columns(dataframe=icephys_meta_df, inplace=True)
# Display the DataFrame in the html docs
icephys_meta_df


#######################
# Useful additional data preparations
# -----------------------------------
#
# Expanding TimeSeriesReference columns
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#
# For query purposes it can be useful to expand the stimulus and response columns to separate the
# (start, count, TimeSeries) values in separate columns.

# Expand the ('stimuli', 'stimulus') to a DataFrame with 3 columns
stimulus_df = pandas.DataFrame(icephys_meta_df[('stimuli', 'stimulus')].tolist(),
                               columns=[('stimuli', 'idx_start'), ('stimuli', 'count'), ('stimuli', 'stimulus')],
                               index=icephys_meta_df.index)
# Remove the original ('stimuli', 'stimulus')  from the icephys_meta_df dataframe
icephys_meta_df.drop(labels=[('stimuli', 'stimulus'), ], axis=1, inplace=True)
# Add our expanded columns to the icephys_meta_df dataframe
icephys_meta_df = pandas.concat([icephys_meta_df, stimulus_df], axis=1)
# display the table for the HTML docs
icephys_meta_df

#######################
# We can then easily expand also the ``(responses, response)`` column in the same way

response_df = pandas.DataFrame(icephys_meta_df[('responses', 'response')].tolist(),
                               columns=[('responses', 'idx_start'), ('responses', 'count'), ('responses', 'response')],
                               index=icephys_meta_df.index)
icephys_meta_df.drop(labels=[('responses', 'response'), ], axis=1, inplace=True)
icephys_meta_df = pandas.concat([icephys_meta_df, response_df], axis=1)


#######################
# Adding Stimulus/Response Metadata
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#
# With all TimeSeries stimuli and responses list in the table we can easily iterate over the
# TimeSeries  to expand our table with additional columns with information from the TimeSeries, e.g.,
# the ``neurodata_type`` or ``name`` or any other properties we may wish to extract from our
# stimulus and response TimeSeries (e.g., ``rate``, ``starting_time``, ``gain`` etc.).
# Here we show a few examples.

# Add a column with the name of the stimulus TimeSeries object.
# Note: We use getattr here to easily deal with missing values, i.e., cases where no stimulus is present
icephys_meta_df[('stimuli', 'name')] = [getattr(s, 'name', None) for s in icephys_meta_df[('stimuli', 'stimulus')]]
# Often we can easily do this in bulk-fashion by specifing the collection of fields of interest
for field in ['neurodata_type', 'gain', 'rate', 'starting_time', 'object_id']:
    icephys_meta_df[('stimuli', field)] = [getattr(s, field, None) for s in icephys_meta_df[('stimuli', 'stimulus')]]
icephys_meta_df

#######################
# Naturally we can again do the same also for our response columns
for field in ['name', 'neurodata_type', 'gain', 'rate', 'starting_time', 'object_id']:
    icephys_meta_df[('responses', field)] = [getattr(s, field, None)
                                             for s in icephys_meta_df[('responses', 'response')]]

#######################
# And we can use the same process to also gather additional metadata about the
# :py:class:`~pynwb.icephys.IntracellularElectrode`, :py:class:`~pynwb.device.Device` and others
for field in ['name', 'device', 'object_id']:
    icephys_meta_df[('electrodes', field)] = [getattr(s, field, None)
                                              for s in icephys_meta_df[('electrodes', 'electrode')]]

#######################
# This basic approach allows us to easily collect all data needed for query in a convenient
# spreadsheet for display, query, and analysis.

#######################
# Performing common metadata queries
# ----------------------------------
#
# With regard to the experiment metadata tables, many of the queries we identified based on
# feed back from the community follow the model of: *"Given X return Y"*, e.g:
#
# * Given a particular stimulus return:
#    * the corresponding response
#    * the corresponding electrode
#    * the stimulus type
#    * all stimuli/responses recorded at the same time (i.e., during the same simultaneous recording)
#    * all stimuli/responses recorded during the same sequential recording
# * Given a particular response return:
#    * the corresponding stimulus
#    * the corresponding electrode
#    * all stimuli/responses recorded at the same time (i.e., during the same simultaneous recording)
#    * all stimuli/responses recorded during the same sequential recording
# * Given an electrode return:
#    * all responses (and stimuli) related to the electrode
#    * all sequential recordings (a.k.a., sweeps) recorded with the electrode
# * Given a stimulus type return:
#    * all related stimulus/response recordings
#    * all the repetitions in which it is present
# * Given a stimulus type and a repetition
#   * get all the responses
# * Given a simultaneous recording (a.k.a., sweep) return:
#   * the repetition/condition/sequential recording it belongs to
#   * all other simultaneous recordings that are part of the same repetition
#   * the experimental condition the simultaneous recording is part of
# * Given a repetitions return:
#   * the experimental condition the simultaneous recording is part of
#   * all sequential- and/or simultaneous recordings within that repetition
# * Given an experimental condition return:
#   * All corresponding repetitions or sequential/simultaneous/intracellular recordings
# * Get the list of all stimulus types
#
# More complex analytics will then commonly combine multiple such query constraints to further process
# the corresponding data, e.g.,
#
# * Given a stimulus and a condition, return all simultaneous recordings (a.k.a sweeps) across repetitions
#   and average the responses
#
# Generally, many of the queries involve looking up a piece of information in on table (e.g., finding
# a stimulus type in :py:class:`~pynwb.icephys.SequentialRecordingsTable`) and then querying for
# related information in child tables (by following the :py:class:`~hdmf.common.table.DynamicTableRegion` links
# included in the corresponding rows) to look up more specific information (e.g., all recordings related to
# the stimulus type) or alternatively querying for related information in parent tables (by finding rows in the
# parent table that link to our rows) and then looking up more general information (e.g., information about the
# experimental condition). Using this approach, we can resolve the above queries using the individual
# :py:class:`~hdmf.common.table.DynamicTable` objects directly, while loading only the data that is
# absolutely necessary into memory.
#
# With the bulk data stored usually in some form of :py:class:`~pynwb.icephys.PatchClampSeries`, the
# ICEphys metadata tables will usually be comparatively small (in terms of total memory). Once we have created
# our integrated `DataFrame`_ as shown above, performing the queries described above becomes quite simple
# as all links between tables have already been resolved all data has been expanded across all rows.
# In general resolving queries on our "denormalized" table amounts to evaluating one or more conditions
# on one or more columns and then retrieving the rows that match our conditions form the table.
#
# Once we have all metadata in a single table, we can also easily sort the rows of our table based on
# a flexible set of conditions or even cluster rows to compute more advanced groupings of intracellular recordings.
#
# Below we show just a few simple examples:
#
# **Given a response, get the stimulus**
#

# Get a response 'vcs_9' from the file
response = nwbfile.get_acquisition('vcs_9')
# Return all data related to that response, including the stimulus as part of ('stimuli', 'stimulus') column
icephys_meta_df[icephys_meta_df[('responses', 'object_id')] == response.object_id]


#######################
# **Get a list of all stimulus types**
#
unique_stimulus_types = np.unique(icephys_meta_df[('sequential_recordings', 'stimulus_type')])
print(unique_stimulus_types)

#######################
# **Given a stimulus type, get all corresponding intracellular recordings**
#
icephys_meta_df[icephys_meta_df[('sequential_recordings', 'stimulus_type')] == 'StimType_1']
