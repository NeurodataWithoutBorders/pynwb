"""
.. _external_resources_streaming:

Annotating Multiple Streamed NWB Files with a Single HERD
=========================================================

A single :py:class:`~pynwb.resources.HERD` can hold external resource references for many
:py:class:`~pynwb.file.NWBFile` objects at once. This makes it possible to build a shared set of
ontology annotations across an entire dataset, for example every file in a
`DANDI <https://dandiarchive.org/>`_ dandiset.

This example streams each NWB file in a dandiset directly from the DANDI Archive (without
downloading the full files) and adds references for two pieces of metadata in each file: the
subject species (mapped to the `NCBI Taxonomy <https://www.ncbi.nlm.nih.gov/taxonomy>`_) and the
experimenter (mapped to an `ORCID <https://orcid.org/>`_ iD). Because a HERD can be saved
independently of any one file with :py:meth:`~hdmf.common.resources.HERD.to_zip`, the resulting
HERD can be distributed alongside the dandiset as a standalone annotation layer and later reloaded
with :py:meth:`~hdmf.common.resources.HERD.from_zip` to add further annotations.

For storing a HERD inside a single NWB file, see :ref:`external_resources`.

.. note::

   This example reads data over the network and is not run when the documentation is built. To run
   it yourself, install the ``dandi`` and ``fsspec`` packages:

   .. code-block:: bash

      pip install dandi fsspec aiohttp requests
"""

# sphinx_gallery_thumbnail_path = 'figures/gallery_thumbnails_streaming_external_resources.png'
import h5py
from dandi.dandiapi import DandiAPIClient
from fsspec import filesystem
from fsspec.implementations.cached import CachingFileSystem
from tqdm import tqdm

from pynwb import NWBHDF5IO
from pynwb.resources import HERD

###############################################################################
# Collect the file URLs from DANDI
# --------------------------------
# Use the :py:class:`~dandi.dandiapi.DandiAPIClient` to list the S3 URL of every NWB file in a
# dandiset. Here we use dandiset `000015 <https://dandiarchive.org/dandiset/000015>`_.

dandiset_id = "000015"
with DandiAPIClient() as client:
    dandiset = client.get_dandiset(dandiset_id, "draft")
    urls = [
        asset.get_content_url(follow_redirects=1, strip_query=True)
        for asset in dandiset.get_assets()
    ]

###############################################################################
# Set up streaming
# ----------------
# Create an HTTP filesystem with a local cache so repeated reads do not re-download data.

fs = CachingFileSystem(fs=filesystem("http"), cache_storage="nwb-cache")

###############################################################################
# Populate a single HERD across all files
# ---------------------------------------
# Open each file in read mode and add references for its subject species and experimenter. Before
# adding a reference, :py:meth:`~hdmf.common.resources.HERD.get_entity` checks whether the entity is
# already in the HERD. If it is, the entity is reused by passing ``entity_uri=None`` (the existing
# URI is kept); otherwise the URI is provided so the entity is created once.

herd = HERD()
for url in tqdm(urls):
    with fs.open(url, "rb") as f, h5py.File(f) as h5_file:
        with NWBHDF5IO(file=h5_file) as io:
            read_nwbfile = io.read()

            # reference the subject species
            species = read_nwbfile.subject.species  # "Mus musculus"
            entity = herd.get_entity(entity_id="NCBI_TAXON:10090")
            if entity is not None:
                # the entity is already in the HERD, so reuse it and keep its existing URI
                entity_uri = None
            else:
                # the entity is not yet in the HERD, so provide its URI to create it
                entity_uri = "https://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?mode=Info&id=10090"
            herd.add_ref(
                file=read_nwbfile,
                container=read_nwbfile.subject,
                key=species,
                entity_id="NCBITAXON:10090",
                entity_uri=entity_uri,
            )

            # reference the experimenter, an attribute of the NWBFile itself
            experimenter = read_nwbfile.experimenter[0]  # "Chen, Tsai-Wen"
            entity = herd.get_entity(entity_id="0000-0001-6782-3819")
            if entity is not None:
                # the entity is already in the HERD, so reuse it and keep its existing URI
                entity_uri = None
            else:
                # the entity is not yet in the HERD, so provide its URI to create it
                entity_uri = "https://orcid.org/0000-0001-6782-3819"
            herd.add_ref(
                file=read_nwbfile,
                container=read_nwbfile,
                attribute="experimenter",
                key=experimenter,
                entity_id="0000-0001-6782-3819",
                entity_uri=entity_uri,
            )

###############################################################################
# Inspect and save the combined HERD
# ----------------------------------
# The flattened table now contains one row per (file, object, key, entity) association across all of
# the streamed files. Save the HERD as a standalone zip archive that can be shared alongside the
# dandiset.

herd.to_dataframe()
herd.to_zip(path="./dandiset_resources.zip")

###############################################################################
# Load an external HERD to annotate a file
# ----------------------------------------
# A HERD saved to a zip archive can be loaded later with
# :py:meth:`~hdmf.common.resources.HERD.from_zip` and used to add further annotations. Here we load
# the HERD we just saved, stream one of the files again, and annotate its institution with the
# corresponding `Research Organization Registry (ROR) <https://ror.org/>`_ identifier.

loaded_herd = HERD.from_zip(path="./dandiset_resources.zip")

with fs.open(urls[0], "rb") as f, h5py.File(f) as h5_file:
    with NWBHDF5IO(file=h5_file) as io:
        read_nwbfile = io.read()
        institution = read_nwbfile.institution  # "Janelia Research Campus"
        loaded_herd.add_ref(
            file=read_nwbfile,
            container=read_nwbfile,
            attribute="institution",
            key=institution,
            entity_id="ROR:013sk6x84",
            entity_uri="https://ror.org/013sk6x84",
        )

loaded_herd.to_dataframe()

###############################################################################
# To view the annotations for a single object, use
# :py:meth:`~hdmf.common.resources.HERD.get_object_entities`. Here we view the species annotation
# stored for the subject of the file we just streamed:

loaded_herd.get_object_entities(container=read_nwbfile.subject)

###############################################################################
# Save the updated HERD as a new zip archive so the added institution annotation is persisted
# alongside the original references.

loaded_herd.to_zip(path="./dandiset_resources_updated.zip")
