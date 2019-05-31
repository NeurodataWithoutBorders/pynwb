..  _extracting_spec:

================================================================
Extracting the specification for different programming languages
================================================================

Projects which don't use pynwb for reading/writing NWB files may still want to
embed the specification into their NWB files for documentation and validation
purposes.

The following python script creates a NWB file and extracts the stored
specification in JSON format as files on disc. The naming scheme of these files is
`${top_level_group}_${namespace}_${nwb_version}_${sub_groups}.json`.

.. literalinclude:: ../code/extracting-specification.py
  :language: python
  :linenos:
  :lines: 6-

See also the `NWB storage
specification <https://nwb-storage.readthedocs.io/en/latest/storage_hdf5.html#caching-format-specifications>`_
for more information on the cached specification.
