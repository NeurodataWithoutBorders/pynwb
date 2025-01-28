======================
How to Make a Tutorial
======================

Tutorials are define using `sphinx-gallery <https://sphinx-gallery.github.io/>`_.
The sources of tutorials are stored in ``docs/gallery`` with each subfolder corresponding
to a subsection in the tutorial gallery.


Create a new tutorial
---------------------

1. Add a new python file to the appropriate subfolder of ``docs/gallery``.

.. hint::

   If you want the output of code cells to be rendered in the docs, then simply
   include the prefix ``plot_`` as part of the name of tutorial file. Tutorials
   without the prefix will render just the code cells and text.

2. Add the names of any files created by running the python file to the
   ``files_to_remove`` variable in ``clean_up_tests()`` in ``test.py``. This function
   will remove the created output files after the sphinx-gallery tests are completed.

2. **Optional:** To specify an explicit position for your tutorial in the subsection of the
   gallery, update the ``GALLERY_ORDER`` variable of the ``CustomSphinxGallerySectionSortKey``
   class defined in ``docs/source/conf.py``. If you skip this step, the tutorial will
   be added in alphabetical order.


3. Check that the docs are building correctly and fix any errors

.. code-block::

   cd docs
   make html

4. View the docs to make sure your gallery renders correctly

.. code-block::

   open docs/_build/html/index.html

5. Make a PR to request addition of your tutorial

Create a new tutorial collection
---------------------------------

To add a section to the tutorial gallery

1. Create a new folder in ``docs/gallery/<new-section>``

2. Create a ``docs/gallery/<new-section>/README.txt`` file with the anchor name and title of the section, e.g.:

.. code-block::

    .. _my-new-tutorials:

    My new tutorial section
    -----------------------

3. Add tutorials to the section by adding the tutorial files to the new folder
