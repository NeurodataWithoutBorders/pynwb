.. _external_resources_entity_guide:

Choosing ``entity_id`` and ``entity_uri`` for external references
=================================================================

When you annotate data with an external resource using
:py:meth:`HERD.add_ref <hdmf.common.resources.HERD.add_ref>`, each reference records two
fields that identify the external term:

``entity_id``
    A compact identifier (a `CURIE <https://www.w3.org/TR/curie/>`_) of the form
    ``prefix:identifier`` (e.g. ``NCBITaxon:10090``). The ``prefix`` names the registry or
    ontology and the ``identifier`` is the term's accession within it.

``entity_uri``
    The full URL that the ``entity_id`` resolves to — a persistent, dereferenceable web
    address for that exact term.

Recommended practice
---------------------

#. **Use a CURIE for** ``entity_id``. Prefer an identifier whose ``prefix`` is registered with
   `bioregistry.io <https://bioregistry.io>`_. The Bioregistry is a comprehensive registry of
   prefixes that maps each CURIE to a canonical, resolvable URL, which avoids the ambiguity of
   the many overlapping identifier schemes (e.g. ``NCBITaxon`` vs. ``taxonomy`` vs.
   ``NCBI_TAXON``).

#. **Use the resolved URL for** ``entity_uri``. The ``entity_uri`` should be the URL that the
   CURIE resolves to. You can look this up by resolving the CURIE through the Bioregistry:
   visiting ``https://bioregistry.io/<entity_id>`` (for example
   ``https://bioregistry.io/NCBITaxon:10090``) redirects to the canonical provider URL, which is
   the value to store in ``entity_uri``.

Keeping ``entity_id`` and ``entity_uri`` consistent in this way means a reader can both
recognize the registry from the compact ``entity_id`` and dereference the ``entity_uri`` to land
on an authoritative description of the term.

Commonly used registries
-------------------------

All of the registries below are registered with the Bioregistry. The ``entity_uri`` column shows
the canonical URL the example ``entity_id`` resolves to.

.. list-table::
   :header-rows: 1
   :widths: 12 26 26 36

   * - Prefix
     - Use for
     - Example ``entity_id``
     - Example ``entity_uri``
   * - ``NCBITaxon``
     - Species
     - ``NCBITaxon:10090``
     - ``http://purl.obolibrary.org/obo/NCBITaxon_10090``
   * - ``ROR``
     - Organizations / institutions
     - ``ROR:013meh722``
     - ``https://ror.org/013meh722``
   * - ``ORCID``
     - People (researchers)
     - ``ORCID:0000-0002-1825-0097``
     - ``https://orcid.org/0000-0002-1825-0097``
   * - ``UBERON``
     - Brain regions (cross-species)
     - ``UBERON:0001950``
     - ``http://purl.obolibrary.org/obo/UBERON_0001950``
   * - ``MBA``
     - Brain regions (Allen Mouse Brain Atlas)
     - ``MBA:385``
     - ``https://purl.brain-bican.org/ontology/mbao/MBA_385``
   * - ``HBA``
     - Brain regions (Allen Human Brain Atlas)
     - ``HBA:4005``
     - ``https://purl.brain-bican.org/ontology/hbao/HBA_4005``
   * - ``DANDI``
     - Dandisets
     - ``DANDI:000015``
     - ``https://dandiarchive.org/dandiset/000015``

Example
-------

.. code-block:: python

    # the species of the subject, mapped to NCBI Taxonomy
    herd.add_ref(
        container=nwbfile.subject,
        attribute="species",
        key="Mus musculus",
        entity_id="NCBITaxon:10090",
        entity_uri="http://purl.obolibrary.org/obo/NCBITaxon_10090",
    )

Resources without individually resolvable URLs
----------------------------------------------

Some resources do not provide a dereferenceable URL for each individual term. For example, many
brain atlases (such as the macaque **D99** atlas) publish a single document or download for the
whole atlas rather than one persistent URL per region.

In that case:

* Put the **URL of the resource as a whole** in ``entity_uri`` (e.g. the atlas's landing or
  download page).
* Put the resource's **identifier for the specific term** — for example, the brain area ID used
  by the atlas — in ``entity_id``.

This keeps every reference dereferenceable to *something* authoritative (the resource) while
still recording the precise term identifier, even when a per-term URL does not exist.

.. code-block:: python

    # a region from an atlas that has no per-region URL: identify the region by its
    # atlas-specific ID and point entity_uri at the atlas itself
    herd.add_ref(
        container=electrodes_table,
        attribute="location",
        key="area_42",
        entity_id="42",
        entity_uri="https://afni.nimh.nih.gov/pub/dist/atlases/macaque/D99_macaque/",
    )

.. seealso::

   :py:class:`HERD <hdmf.common.resources.HERD>` for the full API, and
   :py:meth:`HERD.add_ref <hdmf.common.resources.HERD.add_ref>` for adding references.
