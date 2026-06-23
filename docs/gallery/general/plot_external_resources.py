"""
.. _external_resources:

Linking to External Resources (HERD)
====================================

The :py:class:`~pynwb.resources.HERD` (HDMF External Resources Data Structure) class lets you map
terms used in your data to entities defined in external, web-accessible resources such as
ontologies. For example, you may store a species name ``"Mus musculus"`` on a
:py:class:`~pynwb.file.Subject` and want to link it to the corresponding NCBI Taxonomy term so that
the value is standardized and easy to query.

From a user's perspective, a HERD can be treated as a single table that associates a ``key`` (a term
used on an ``object``, i.e. a dataset or attribute in the file) with an ``entity`` (a term in an
external resource, identified by a compact URI and a full URI). Internally, HERD stores this in six
interlinked tables (``keys``, ``files``, ``entities``, ``entity_keys``, ``objects``, and
``object_keys``) and provides convenience methods so you rarely need to interact with those tables
directly.

This tutorial shows how to create a HERD, annotate objects in an NWB file, store the HERD in the
file, and inspect the annotations after reading the file back. For the full HERD API (including
``add_ref_termset`` for validating terms against a :py:class:`~hdmf.term_set.TermSet`, ``get_key``,
and compound-data references), see the
`HDMF HERD tutorial <https://hdmf.readthedocs.io/en/stable/tutorials/plot_external_resources.html>`_.
"""

# sphinx_gallery_thumbnail_path = 'figures/gallery_thumbnails_external_resources.png'
import os
from datetime import datetime
from uuid import uuid4

from dateutil.tz import tzlocal

from pynwb import NWBHDF5IO, NWBFile
from pynwb.file import Subject
from pynwb.resources import HERD

###############################################################################
# Create an NWB file
# ------------------
# Start with an :py:class:`~pynwb.file.NWBFile` that has a :py:class:`~pynwb.file.Subject`. The
# subject's species is the value we will annotate with an external resource.

nwbfile = NWBFile(
    session_description="a demonstration of external resources",
    identifier=str(uuid4()),
    session_start_time=datetime(2018, 4, 25, 2, 30, 3, tzinfo=tzlocal()),
    subject=Subject(subject_id="001", species="Mus musculus"),
)

###############################################################################
# Create a HERD and attach it to the file
# ---------------------------------------
# Create a :py:class:`~pynwb.resources.HERD` and assign it to the ``external_resources`` field of the
# :py:class:`~pynwb.file.NWBFile`.

nwbfile.external_resources = HERD()

###############################################################################
# Add references with ``add_ref``
# -------------------------------
# Use :py:meth:`~hdmf.common.resources.HERD.add_ref` to add a row that links a key on an object to an
# external entity. Here we link the subject's species to the NCBI Taxonomy entry for *Mus musculus*.
# Because the subject is already part of the file, the ``file`` argument is resolved automatically
# from the parent hierarchy and can be omitted.

nwbfile.external_resources.add_ref(
    container=nwbfile.subject,
    key=nwbfile.subject.species,
    entity_id="NCBI_TAXON:10090",
    entity_uri="https://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?mode=Info&id=10090",
)

###############################################################################
# References can also point to an attribute of an object, such as a column of a table. Here we record
# the brain region of a set of electrodes in the electrodes table and link the region to the
# corresponding structure in the
# `Allen Mouse Brain Common Coordinate Framework (CCFv3) <https://atlas.brain-map.org/>`_. When the
# target is a column, pass the table as the ``container`` and the column name as the ``attribute``;
# HERD resolves the reference to the column object itself, which is the closest object that has a
# data type.

device = nwbfile.create_device(name="probe")
electrode_group = nwbfile.create_electrode_group(
    name="shank0",
    description="a shank of the recording probe",
    location="VISp",
    device=device,
)
for _ in range(4):
    nwbfile.add_electrode(location="VISp", group=electrode_group)

nwbfile.external_resources.add_ref(
    container=nwbfile.electrodes,
    attribute="location",
    key="VISp",
    entity_id="385",
    entity_uri="https://api.brain-map.org/api/v2/data/Structure/385.json",
)

###############################################################################
# Inspect the HERD
# ----------------
# :py:meth:`~hdmf.common.resources.HERD.to_dataframe` flattens the interlinked tables into a single
# :py:class:`~pandas.DataFrame`, with one row per (object, key, entity) association.

nwbfile.external_resources.to_dataframe()

###############################################################################
# You can also view the individual tables. Each is a
# :py:class:`~hdmf.common.table.DynamicTable` and has its own ``to_dataframe`` method.

nwbfile.external_resources.keys.to_dataframe()

###############################################################################

nwbfile.external_resources.entities.to_dataframe()

###############################################################################
# :py:meth:`~hdmf.common.resources.HERD.get_object_type` returns all annotations for objects of a
# given type, for example every annotated :py:class:`~pynwb.file.Subject`.

nwbfile.external_resources.get_object_type(object_type="Subject")

###############################################################################
# Write and read the NWB file
# ---------------------------
# Writing the file stores the HERD inside it. Reading the file back makes the HERD available again
# through the ``external_resources`` field.

filename = "external_resources_tutorial.nwb"
with NWBHDF5IO(filename, mode="w") as io:
    io.write(nwbfile)

read_io = NWBHDF5IO(filename, mode="r")
read_nwbfile = read_io.read()
read_herd = read_nwbfile.external_resources

###############################################################################
# Access the loaded data
# -----------------------
# In a Jupyter notebook, the default display of a read HERD shows collapsible sections that can
# appear empty. To see the annotations, use the same accessors as above:
# :py:meth:`~hdmf.common.resources.HERD.to_dataframe` for the flattened view, or the individual
# tables for a focused view.

read_herd.to_dataframe()

###############################################################################
# View the individual tables:

read_herd.keys.to_dataframe()

###############################################################################

read_herd.entities.to_dataframe()

###############################################################################
# :py:meth:`~hdmf.common.resources.HERD.get_object_entities` returns the entities annotated on a
# single object as a :py:class:`~pandas.DataFrame`. On a HERD read back from a file this accessor
# currently requires the fix for
# `hdmf #1496 <https://github.com/hdmf-dev/hdmf/issues/1496>`_, which will be resolved soon, so it is
# shown here commented out:

# read_herd.get_object_entities(container=read_nwbfile.subject)

###############################################################################
# Close the file once you are done reading from it.

read_io.close()

###############################################################################
# Alternative: store a HERD outside an NWB file
# ---------------------------------------------
# A HERD can also be saved independently of an NWB file as a zip archive of the underlying tables
# using :py:meth:`~hdmf.common.resources.HERD.to_zip`, and read back with
# :py:meth:`~hdmf.common.resources.HERD.from_zip`. This is useful when external resources span
# multiple files; see :ref:`external_resources_streaming` for an example that annotates many NWB
# files with a single HERD. For the full HERD API, see the
# `HDMF HERD tutorial <https://hdmf.readthedocs.io/en/stable/tutorials/plot_external_resources.html>`_.

os.remove(filename)
