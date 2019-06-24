=====================
How to Make a Release
=====================

A core developer should use the following steps to create a release `X.Y.Z` of **pynwb**.

.. note::

  Since the pynwb wheels do not include compiled code, they are considered
  *pure* and could be generated on any supported platform.

  That said, considering the instructions below have been tested on a Linux system,
  they may have to be adapted to work on macOS or Windows.

-------------
Prerequisites
-------------

* All CI tests are passing on `CircleCI`_ and `Azure Pipelines`_.

* You have a `GPG signing key <https://help.github.com/articles/generating-a-new-gpg-key/>`_.

-------------------------
Documentation conventions
-------------------------

The commands reported below should be evaluated in the same terminal session.

Commands to evaluate starts with a dollar sign. For example::

  $ echo "Hello"
  Hello

means that ``echo "Hello"`` should be copied and evaluated in the terminal.

----------------------
Setting up environment
----------------------

1. First, `register for an account on PyPI <https://pypi.org>`_.


2. If not already the case, ask to be added as a ``Package Index Maintainer``.


3. Create a ``~/.pypirc`` file with your login credentials::

    [distutils]
    index-servers =
      pypi
      pypitest

    [pypi]
    username=<your-username>
    password=<your-password>

    [pypitest]
    repository=https://test.pypi.org/legacy/
    username=<your-username>
    password=<your-password>

  where ``<your-username>`` and ``<your-password>`` correspond to your PyPI account.


------------------
PyPI: Step-by-step
------------------

1. Make sure that all CI tests are passing on `CircleCI`_ and `Azure Pipelines`_.


2. List all tags sorted by version

  .. code::

    $ git tag -l | sort -V


3. Choose the next release version number

  .. code::

    $ release=X.Y.Z

  .. warning::

      To ensure the packages are uploaded on `PyPI`_, tags must match this regular
      expression: ``^[0-9]+(\.[0-9]+)*(\.post[0-9]+)?$``.


4. Download latest sources

  .. code::

    $ cd /tmp && git clone git@github.com:NeurodataWithoutBorders/pynwb && cd pynwb


5. Tag the release

  .. code::

    $ git tag --sign -m "pynwb ${release}" ${release} origin/dev

  .. warning::

      This step requires a `GPG signing key <https://help.github.com/articles/generating-a-new-gpg-key/>`_.


6. Publish the release tag

  .. code::

    $ git push origin ${release}

  .. important::

      This will trigger builds on each CI services and automatically upload the wheels
      and source distribution on `PyPI`_.


7. Check the status of the builds on `CircleCI`_ and `Azure Pipelines`_.


8. Once the builds are completed, check that the distributions are available on `PyPI`_ and that
   a new `GitHub release <https://github.com/NeurodataWithoutBorders/pynwb/releases>`_ was created.


9. Create a clean testing environment to test the installation

  .. code::

    $ mkvirtualenv pynwb-${release}-install-test && \
      pip install pynwb && \
      python -c "import pynwb; print(pynwb.__version__)"

  .. note::

      If the ``mkvirtualenv`` command is not available, this means you do not have `virtualenvwrapper`_
      installed, in that case, you could either install it or directly use `virtualenv`_ or `venv`_.

10. Cleanup

  .. code::

    $ deactivate  && \
      rm -rf dist/* && \
      rmvirtualenv pynwb-${release}-install-test


.. _virtualenvwrapper: https://virtualenvwrapper.readthedocs.io/
.. _virtualenv: http://virtualenv.readthedocs.io
.. _venv: https://docs.python.org/3/library/venv.html

.. _AppVeyor: https://ci.appveyor.com/project/NeurodataWithoutBorders/pynwb/history
.. _CircleCI: https://circleci.com/gh/NeurodataWithoutBorders/pynwb
.. _Travis CI: https://travis-ci.org/NeurodataWithoutBorders/pynwb/builds
.. _Azure Pipelines: https://dev.azure.com/NeurodataWithoutBorders/pynwb/_build?definitionId=3

.. _PyPI: https://pypi.org/project/pynwb

-------------------
Conda: Step-by-step
-------------------

.. warning::

   Publishing on conda requires you to have corresponding package version uploaded on
   `PyPI`_. So you have to do the PypI and Github release before you do the conda release.

In order to release a new version on conda-forge, follow the steps below:

1. Choose the next release version number (that matches with the pypi version that you already published)

  .. code::

    $ release=X.Y.Z

2. Fork pynwb-feedstock

 First step is to fork `pynwb-feedstock <https://github.com/conda-forge/pynwb-feedstock>`_ repository.
 This is the recommended `best practice <https://conda-forge.org/docs/conda-forge_gotchas.html#using-a-fork-vs-a-branch-when-updating-a-recipe>`_  by conda.


3. Clone forked feedstock

   Fill the YOURGITHUBUSER part.

   .. code::

      $ cd /tmp && git clone https://github.com/YOURGITHUBUSER/pynwb-feedstock.git


4. Download corresponding source for the release version

  .. code::

    $ cd /tmp && \
      wget https://github.com/NeurodataWithoutBorders/pynwb/releases/download/$release/pynwb-$release.tar.gz

5. Create a new branch

   .. code::

      $ cd pynwb-feedstock && \
        git checkout -b $release


6. Modify ``meta.yaml``

   Update the `version string <https://github.com/conda-forge/pynwb-feedstock/blob/master/recipe/meta.yaml#L2>`_ and
   `sha256 <https://github.com/conda-forge/pynwb-feedstock/blob/master/recipe/meta.yaml#L3>`_.

   We have to modify the sha and the version string in the ``meta.yaml`` file.

   For linux flavors:

   .. code::

      $ sed -i "2s/.*/{% set version = \"$release\" %}/" recipe/meta.yaml
      $ sha=$(openssl sha256 /tmp/pynwb-$release.tar.gz | awk '{print $2}')
      $ sed -i "3s/.*/{$ set sha256 = \"$sha\" %}/" recipe/meta.yaml

   For macOS:

   .. code::

      $ sed -i -- "2s/.*/{% set version = \"$release\" %}/" recipe/meta.yaml
      $ sha=$(openssl sha256 /tmp/pynwb-$release.tar.gz | awk '{print $2}')
      $ sed -i -- "3s/.*/{$ set sha256 = \"$sha\" %}/" recipe/meta.yaml



7. Push the changes

   .. code::

      $ git push origin $release

8. Create a Pull Request

   Create a pull request against the `main repository <https://github.com/conda-forge/pynwb-feedstock/pulls>`_. If the tests are passed
   a new release will be published on Anaconda cloud.
