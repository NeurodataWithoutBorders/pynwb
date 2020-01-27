..  _software_process:

================
Software Process
================

----------------------
Continuous Integration
----------------------

PyNWB is tested against Ubuntu, macOS, and Windows operating systems.
The project has both unit and integration tests.

* CircleCI_ runs all PyNWB tests on Ubuntu
* `Azure Pipelines`_ runs all PyNWB tests on Windows and macOS

Each time a PR is published or updated, the project is built, packaged, and tested on all supported operating systems
and python distributions. That way, as a contributor, you know if you introduced regressions or coding style
inconsistencies.

There are badges in the README_ file which shows the current condition of the dev branch.

.. _CircleCI: https://circleci.com/gh/NeurodataWithoutBorders/workflows/pynwb
.. _Azure Pipelines: https://dev.azure.com/NeurodataWithoutBorders/pynwb/_build
.. _README: https://github.com/NeurodataWithoutBorders/pynwb#readme


--------
Coverage
--------

Coverage is computed and reported using the coverage_ tool. There is a badge in the README_ file which
shows percentage coverage. A detailed report can be found on codecov_ which shows line by line which
lines are covered by the tests.

.. _coverage: https://coverage.readthedocs.io
.. _codecov: https://codecov.io/gh/NeurodataWithoutBorders/pynwb/tree/dev/src/pynwb

..  _software_process_requirement_specifications:


--------------------------
Requirement Specifications
--------------------------

There are 4 kinds of requirements specification in PyNWB.

Setup.py Dependencies
---------------------

There are 4 kinds of requirements specification in PyNWB.

The first one is the requirements-min.txt_ file, which lists the package dependencies and their minimum versions for
installing PyNWB. These dependencies are read by setup.py_ into the `install_requires` key, with the adjustment that
the `'=='` listed in `requirements-min.txt` are replaced with `'>='` to reflect that they are minimum versions.

The second one is requirements.txt_ which contain a list of pinned (concrete) dependencies to reproduce
an entire development environment to use PyNWB.

The third one is requirements-dev.txt_ which contain a list of pinned (concrete) dependencies to reproduce
an entire development environment to use PyNWB, run PyNWB tests, check code style, compute coverage, and create test
environments.

The final one is requirements-doc.txt_ which contain a list of dependencies to generate the documentation for PyNWB.
Both this file and `requirements.txt` are used by ReadTheDocs_ to initialize the local environment for Sphinx to run.

In order to check the status of the required packages, requires.io_ is used to create a badge on the project
README_. If all the required packages are up to date, a green badge appears.

If some of the packages are outdated, see :ref:`update_requirements_files`.

.. _requirements-min.txt: https://github.com/NeurodataWithoutBorders/pynwb/blob/dev/requirements-min.txt
.. _setup.py: https://github.com/NeurodataWithoutBorders/pynwb/blob/dev/setup.py
.. _requirements.txt: https://github.com/NeurodataWithoutBorders/pynwb/blob/dev/requirements.txt
.. _requirements-dev.txt: https://github.com/NeurodataWithoutBorders/pynwb/blob/dev/requirements-dev.txt
.. _requirements-doc.txt: https://github.com/NeurodataWithoutBorders/pynwb/blob/dev/requirements-doc.txt
.. _ReadTheDocs: https://readthedocs.org/projects/pynwb/
.. _requires.io: https://requires.io/github/NeurodataWithoutBorders/pynwb/requirements/?branch=dev


-------------------------
Versioning and Releasing
-------------------------

PyNWB uses versioneer_ for versioning source and wheel distributions. Versioneer creates a semi-unique release
name for the wheels that are created. It requires a version control system (git in PyNWB's case) to generate a release
name. After all the tests pass, CircleCI creates both a wheel (\*.whl) and source distribution (\*.tar.gz) for Python 3
and uploads them back to GitHub as a release_. Versioneer makes it possible to get the source distribution from GitHub
and create wheels directly without having to use a version control system because it hardcodes versions in the source
distribution.

It is important to note that GitHub automatically generates source code archives in .zip and .tar.gz formats and
attaches those files to all releases as an asset. These files currently do not contain the submodules within PyNWB and
thus do not serve as a complete installation. For a complete source code archive, use the source distribution generated
by CircleCI, typically named `pynwb-{version}.tar.gz`.

.. _versioneer: https://github.com/warner/python-versioneer
.. _release: https://github.com/NeurodataWithoutBorders/pynwb/releases
