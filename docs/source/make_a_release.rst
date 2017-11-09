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

* All CI tests are passing on all platforms.

* You have a `GPG signing key <https://help.github.com/articles/generating-a-new-gpg-key/>`_.

* You have the API key associated with `<https://github.com/nwb-bot>`_.

----------
Convention
----------

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


------------
Step-by-step
------------

1. Choose the next release version number::

    $ release=X.Y.Z


2. Download latest sources::

    $ cd /tmp && git clone git@github.com:NeurodataWithoutBorders/pynwb


3. Tag the release::

    $ git tag -s -m "pynwb ${release}" ${release} origin/dev

    *Requires a GPG signing key*


4. Create a new virtual environment and install release requirements::

    $ mkvirtualenv pynwb-${release}-release
    $ pip install tox twine


5. Create source distribution and wheels::

    $ rm -rf dist/
    $ tox
      [...]
      py35: commands succeeded
      py27: commands succeeded
      congratulations :)

   .. warning::

     Move forward **only** if the ``tox`` command completed successfully. If not,
     abort the release process and report the problem.


6. Confirm that expected packages have been generated::

    $ ls -1 dist/*
    pynwb-X.Y.Z-py2-none-any.whl
    pynwb-X.Y.Z-py3-none-any.whl
    pynwb-X.Y.Z.tar.gz

  .. note::

    ``X.Y.Z`` correspond to the release version selected earlier.


7. Sign and upload the packages to the PyPI testing server::

    $ twine upload --sign -r pypitest dist/*

  .. warning::

    Confirm that the packages are available on both testing servers:

    - pre-production: `<https://test.pypi.org/project/pynwb/>`_
    - legacy: `<https://testpypi.python.org/pypi/pynwb>`_.


8. Upload the packages to the production PyPI server::

    $ twine upload dist/*

  .. warning::

    Confirm that the packages are available on both servers:

    - pre-production: `<https://pypi.org/project/pynwb/>`_
    - legacy: `<https://pypi.python.org/pypi/pynwb>`_


9. Create a clean testing environment to test installation::

    $ mkvirtualenv pynwb-${release}-install-test
    $ pip install pynwb


10. Publish the release tag::

    $ git push origin ${release}


11. Create GitHub release and upload packages::

   $ pip install githubrelease
   $ export GITHUB_TOKEN=<NWBOT_API_KEY>
   $ githubrelease release NeurodataWithoutBorders/pynwb create ${release} --name ${release} --publish ./dist/*


12. Cleanup::

    $ deactivate
    $ rm -rf dist/*
    $ rmvirtualenv pynwb-${release}-release
    $ rmvirtualenv pynwb-${release}-install-test

