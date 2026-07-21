..  _software_process:

================
Software Process
================

----------------------
Continuous Integration
----------------------

PyNWB is tested against Ubuntu, macOS, and Windows operating systems.
The project has both unit and integration tests.
Tests run on :pynwb:`GitHub Actions <actions>`.

Each time a PR is published or updated, the project is built, packaged, and
tested on all supported operating systems and python distributions. That way,
as a contributor, you know if you introduced regressions or coding style
inconsistencies.

There are badges in the :pynwb:`README <blob/dev/README.rst>` file which shows
the current condition of the dev branch.

--------
Coverage
--------

Code coverage is computed and reported using the coverage_ tool. There are two coverage-related
badges in the :pynwb:`README <blob/dev/README.rst>` file. One shows the status of the :pynwb:`GitHub Action workflow <actions?query=workflow%3A%22Run+coverage%22>` which runs the coverage_ tool and uploads the report to
codecov_, and the other badge shows the percentage coverage reported from codecov_. A detailed report can be found on
codecov_, which shows line by line which lines are covered by the tests.

.. _coverage: https://coverage.readthedocs.io
.. _codecov: https://app.codecov.io/gh/NeurodataWithoutBorders/pynwb/tree/dev/src/pynwb

-------------------------
Installation Requirements
-------------------------

:pynwb:`pyproject.toml <blob/dev/pyproject.toml>` contains a list of package dependencies and their version ranges allowed for
running PyNWB. As a library, upper bound version constraints create more harm than good in the long term (see this
`blog post`_) so we avoid setting upper bounds on requirements.

.. _blog post: https://iscinumpy.dev/post/bound-version-constraints/

--------------------
Testing Requirements
--------------------

Dependencies are declared in :pynwb:`pyproject.toml <blob/dev/pyproject.toml>`. User-facing optional features are
``[project.optional-dependencies]`` extras (``zarr`` and ``termset``, installable with e.g.
``pip install pynwb[zarr]``). Development dependencies are `PEP 735 <https://peps.python.org/pep-0735/>`_
``[dependency-groups]``: ``test`` (test and lint tooling), ``stream`` (streaming dependencies for the optional
tests), and ``docs`` (documentation dependencies).

``tox`` selects these via the ``extras`` and ``dependency_groups`` settings in :pynwb:`tox.ini <blob/dev/tox.ini>`.
The ``upgraded`` environments install the latest compatible dependencies, while the ``minimum`` environments use
``uv pip install --resolution lowest-direct`` to install the lowest compatible versions of the direct dependencies.

:pynwb:`environment-ros3.yml <blob/dev/environment-ros3.yml>` lists the conda dependencies used to test ROS3
streaming in PyNWB.

--------------------------
Documentation Requirements
--------------------------

The documentation dependencies are declared in the ``docs`` dependency group in
:pynwb:`pyproject.toml <blob/dev/pyproject.toml>`. ReadTheDocs_ installs them together with the ``zarr`` and
``termset`` feature extras (``pip install --group docs ".[zarr,termset]"``) so the gallery examples can run.

.. _ReadTheDocs: https://app.readthedocs.org/projects/pynwb/

-------------------------
Versioning and Releasing
-------------------------

PyNWB uses versioneer_ for versioning source and wheel distributions. Versioneer creates a semi-unique release
name for the wheels that are created. It requires a version control system (git in PyNWB's case) to generate a release
name. After all the tests pass, GitHub Actions creates both a wheel (\*.whl) and source distribution (\*.tar.gz) for
Python 3 and uploads them back to GitHub as a :pynwb:`releases`. Pushing to "dev" attaches them to the rolling "latest"
pre-release; pushing a MAJOR.MINOR.PATCH tag attaches them to a release for that tag and uploads them to PyPI.
Versioneer makes it possible to get the source distribution from GitHub
and create wheels directly without having to use a version control system because it hardcodes versions in the source
distribution.

It is important to note that GitHub automatically generates source code archives in .zip and .tar.gz formats and
attaches those files to all releases as an asset. These files currently do not contain the submodules within PyNWB and
thus do not serve as a complete installation. For a complete source code archive, use the source distribution generated
by GitHub Actions, typically named `pynwb-{version}.tar.gz`.

.. _versioneer: https://github.com/python-versioneer/python-versioneer

----------------------------------------------------
Coordinating with nwb-schema Repository and Releases
----------------------------------------------------

The default branch is "dev". It is important that all releases of PyNWB contain a released version of nwb-schema.
If a release contains an unreleased version of nwb-schema, e.g., from an untagged commit on the "dev" branch, then
tracking the identity of the included nwb-schema becomes difficult and the same version string could point to two
different versions of the schema.

Whenever the "dev" branch of the nwb-schema repo is updated, a commit should be made to the "schema_x.y.z" branch of
PyNWB, where "x.y.z" is the upcoming version of nwb-schema, that updates the nwb-schema submodule to the latest commit
of the "dev" branch on nwb-schema. If the update to nwb-schema is the first change after a release, the "schema_x.y.z"
branch should be created, the nwb-schema submodule should be updated, and a draft PR should be made for merging the
"schema_x.y.z" branch to "dev". This PR provides a useful public view into how the API changes with each change to the
schema.

If the change in nwb-schema requires an accompanying change to PyNWB, then a new branch should be made with the
corresponding changes, and a new PR should be made for merging the new branch into the "schema_x.y.z" branch. The PR
should be merged in GitHub's "squash and merge" mode.

When a new version of nwb-schema x.y.z is released, the "schema_x.y.z" branch of PyNWB should be checked to ensure
that the nwb-schema submodule points to the new release-tagged commit of nwb-schema. Then the PR should be merged
into dev with GitHub's "merge" mode. Commits should NOT be squashed because they will usually represent independent
changes to the API or schema, and the git history should reflect those changes separately.

The "dev" branch should NEVER contain unreleased versions of nwb-schema to prevent cases of users and developers
accidentally publishing files with unreleased schema. This problem cannot be completely avoided, however, as users
could still publish files generated from the "schema_x.y.z" branch of PyNWB.

The nwb-schema uses hdmf-common-schema. Changes in hdmf-common-schema that affect nwb-schema result in version
changes of nwb-schema and as such are managed in the same fashion. One main difference is that updates to
hdmf-common-schema may also involve updates to version requirements for HDMF in PyNWB.
