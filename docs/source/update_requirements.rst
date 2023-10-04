
..  _update_requirements_files:

================================
How to Update Requirements Files
================================

The different requirements files introduced in :ref:`software_process` section are the following:

* :pynwb:`requirements.txt <blob/dev/requirements.txt>`
* :pynwb:`requirements-dev.txt <blob/dev/requirements-dev.txt>`
* :pynwb:`requirements-doc.txt <blob/dev/requirements-doc.txt>`
* :pynwb:`requirements-min.txt <blob/dev/requirements-min.txt>`

requirements.txt
================

`requirements.txt` of the project can be created or updated and then captured using
the following script:

.. code::

   mkvirtualenv pynwb-requirements

   cd pynwb
   pip install .
   pip check # check for package conflicts
   pip freeze > requirements.txt

   deactivate
   rmvirtualenv pynwb-requirements


requirements-(dev|doc).txt
==========================

Any of these requirements files can be updated using
the following scripts:

.. code::

   cd pynwb

   # Set the requirements file to update: requirements-dev.txt or requirements-doc.txt
   target_requirements=requirements-dev.txt

   mkvirtualenv pynwb-requirements

   # Install updated requirements
   pip install -U -r $target_requirements

   # If relevant, you could pip install new requirements now
   # pip install -U <name-of-new-requirement>

   # Check for any conflicts in installed packages
   pip check

   # Update list of pinned requirements
   pip freeze > $target_requirements

   deactivate
   rmvirtualenv pynwb-requirements


requirements-min.txt
====================

Minimum requirements should be updated manually if a new feature or bug fix is added in a dependency that is required
for proper running of PyNWB. Minimum requirements should also be updated if a user requests that PyNWB be installable
with an older version of a dependency, all tests pass using the older version, and there is no valid reason for the
minimum version to be as high as it is.
