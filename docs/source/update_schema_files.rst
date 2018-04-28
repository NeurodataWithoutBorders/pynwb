==========================
How to Update Schema Files
==========================

Schema files located in ``src/pynwb/data/`` directory must updated running
the script ``UpdateFromUpstream.sh`` found in that same directory.

::

    $ cd pynwb
    $ git checkout -b update-schema-files
    $ ./src/pynwb/data/UpdateFromUpstream.sh
    $ git push origin update-schema-files

    # Then create a pull request
