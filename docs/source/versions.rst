.. _versions:

PyNWB Versions and HDMF Versions
==========================================

PyNWB relies heavily on the HDMF package which is developed in tandem with PyNWB. Each release of PyNWB is
compatible with particular versions of HDMF.

+----------------+-------------------------+
| PyNWB Version  | Compatible HDMF Version |
+================+=========================+
| 1.4.0          | >=2.1.0, <3             |
+----------------+-------------------------+
| 1.3.3          | >=1.6.4, <2             |
+----------------+-------------------------+
| 1.3.1 to 1.3.2 | >=1.6.2, <2             |
+----------------+-------------------------+
| 1.3.0          | >=1.6.1, <2             |
+----------------+-------------------------+
| 1.2.0 to 1.2.1 | >=1.5.4, <2             |
+----------------+-------------------------+
| 1.1.2          | 1.3.3                   |
+----------------+-------------------------+
| 1.1.1          | 1.3.2                   |
+----------------+-------------------------+
| 1.1.0          | 1.2.0                   |
+----------------+-------------------------+
| 1.0.3          | 1.0.4                   |
+----------------+-------------------------+

PyNWB Versions and NWB Schema Versions
==========================================

Each release of PyNWB is bundled with the latest version of the NWB schema at the time of release (referred to here as
version X). Each release of PyWNB can read any data written with NWB version 2.0.0 to version X and writes data only
in version X.

When modifying existing NWB data, if data written with an NWB version (at least 2.0.0) that is older than X is loaded
by PyNWB and then the data is modified by PyNWB (i.e., calls ``write`` on the IO object), then NWB version X will be
added to the file and the data will be (in most cases) transformed to comply with the newer schema version X.

+----------------+--------------------------+---------------------------+
| PyNWB Version  | Reads NWB Schema Version | Writes NWB Schema Version |
+================+==========================+===========================+
| 1.4.0          | 2.0.0 to 2.2.5           | 2.2.5                     |
+----------------+--------------------------+---------------------------+
| 1.3.2 to 1.3.3 | 2.0.0 to 2.2.5           | 2.2.5                     |
+----------------+--------------------------+---------------------------+
| 1.3.1          | 2.0.0 to 2.2.4           | 2.2.4                     |
+----------------+--------------------------+---------------------------+
| 1.3.0          | 2.0.0 to 2.2.2           | 2.2.2                     |
+----------------+--------------------------+---------------------------+
| 1.2.0 to 1.2.1 | 2.0.0 to 2.2.1           | 2.2.1                     |
+----------------+--------------------------+---------------------------+
| 1.1.0 to 1.1.2 | 2.0.0 to 2.1.0           | 2.1.0                     |
+----------------+--------------------------+---------------------------+
| 1.0.3          | 2.0.0 to 2.0.2           | 2.0.2                     |
+----------------+--------------------------+---------------------------+

For details about changes between NWB schema versions, see the `NWB format release notes
<https://nwb-schema.readthedocs.io/en/latest/format_release_notes.html>`_.

NWB Schema and hdmf-common Schema Versions
=================================================

Each release of the NWB schema is bundled with a particular release of the hdmf-common schema.

Only releases of NWB schema that are used by PyNWB are listed below.

+--------------------+----------------------------+
| NWB Schema Version | hdmf-common Schema Version |
+====================+============================+
| 2.2.2 to 2.2.5     | 1.1.3                      |
+--------------------+----------------------------+
| 2.2.1              | 1.1.2                      |
+--------------------+----------------------------+
| <=2.1.0            | None                       |
+--------------------+----------------------------+

For details about changes between hdmf-common schema versions, see the `hdmf-common release notes
<https://hdmf-common-schema.readthedocs.io/en/latest/format_release_notes.html>`_.

PyNWB Versions and hdmf-common Schema Versions
=================================================

Each release of PyNWB is bundled with a release of the NWB schema, which itself is bundled with a particular
release of the hdmf-common schema. However, PyNWB loads the release of the hdmf-common schema available from the
HDMF package installed locally rather than the bundled release of the hdmf-common schema within the bundled NWB schema.

In PyNWB version 1.4.0, this could lead to an incompatibility between the version of hdmf-common schema (1.1.3)
that is bundled with PyNWB and the version of hdmf-common schema (1.2.0+) used by HDMF.
