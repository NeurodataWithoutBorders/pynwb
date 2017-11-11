
..  _update_requirements_files:

================================
How to Update Requirements Files
================================

The different requirements files introduced in :ref:`software_process` are the following:

.. _requirements.txt: https://github.com/NeurodataWithoutBorders/pynwb/blob/dev/requirements.txt
.. _requirements-dev.txt: https://github.com/NeurodataWithoutBorders/pynwb/blob/dev/requirements-dev.txt
.. _requirements-doc.txt: https://github.com/NeurodataWithoutBorders/pynwb/blob/dev/requirements-doc.txt


section can be updated using
These section explains how to update the multiple requirements files presented in the



Requirements.txt of the project can be created and captured by following the code snippet below:

.. code::

   cd pynwb
   mkvirtualenv pynwb
   pip install .
   pip freeze > requirements.txt