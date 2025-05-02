.. _extension-example-labmetadata:

Extensions for lab-specific metadata: Extending ``LabMetaData``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Use case
""""""""

.. short_description_start

Here we address the use case of adding lab-specific metadata to a file, e.g.,
lab-specific information about experimental protocols, lab-specific identifiers and so on.
This approach is intended for usually small metadata. :bdg-link-primary:`Extension source <https://github.com/NeurodataWithoutBorders/ndx-labmetadata-example>`

.. short_description_end



Approach
""""""""

To include lab-specific metadata, NWB provides :py:class:`pynwb.file.LabMetaData` as a
a convenient base type, which makes it easy to add your data to an :py:class:`pynwb.file.NWBFile`
without having to modify the :py:class:`pynwb.file.NWBFile` type itself
(since adding of :py:class:`pynwb.file.LabMetaData` is already implemented).

.. note::

     NWB uses dynamically extensible table structures based on :py:class:`~hdmf.common.table.DynamicTable`
     to describe metadata and derived results, e.g., :py:class:`~pynwb.epochs.TimeIntervals` for epochs or trials
     or :py:class:`~pynwb.file.ElectrodeTable` to describe extracellular electrodes. Depending on the
     type of metadata, use of these existing dynamic table structures can help avoid the need for
     custom extensions by including the data as additional, custom columns in the appropriate existing tables.

Creating the extension
""""""""""""""""""""""

**1.** Create a new repository for the extension using the :nwb_extension_git:`ndx-template`:

.. code-block:: bash

   cookiecutter gh:nwb-extensions/ndx-template

**2.** Answer a few simple questions of the cookiecutter template. We can respond to many questions
with ``Enter`` to accept the default response (e.g., to start with ``version=0.1.0``):

.. code-block:: none

    namespace [ndx-my-namespace]: ndx-labmetadata-example
    description [My NWB extension]: Example extension to illustrate how to extend LabMetaData for adding lab-specific metadata
    author [My Name]: Oliver Ruebel
    email [my_email@example.com]: oruebel@lbl.gov
    github_username [myname]: oruebel
    copyright [2021, Oliver Ruebel]:
    version [0.1.0]:
    release [alpha]:
    Select license:
    1 - BSD-3
    2 - MIT
    3 - Apache Software License 2.0
    4 - Other
    Choose from 1, 2, 3, 4 [1]: 1
    py_pkg_name [ndx_labmetadata_example]:

**3.** Edit ``ndx-my-brainlabsrc/spec/create_extension_spec.py`` that was generated for you to define the
schema of your extension. See :ref:`extension-spec-api` section for details on how to use the specification API.

* Add ``LabMetaData`` as an include type

.. code-block:: python

    ns_builder.include_type('LabMetaData', namespace='core')

* Define your new ``LabMetaData`` type for your lab

.. code-block:: python

     labmetadata_ext = NWBGroupSpec(
        name='custom_lab_metadata',
        doc='Example extension type for storing lab metadata',
        neurodata_type_def='LabMetaDataExtensionExample',
        neurodata_type_inc='LabMetaData',
    )

* Add the ``Groups``, ``Datasets``, and ``Attributes`` with the metadata specific to our lab to
  our ``LabMetaData`` schema

.. code-block:: python

    labmetadata_ext.add_dataset(
        name="tissue_preparation",
        doc="Lab-specific description of the preparation of the tissue",
        dtype='text',
        quantity='?'
    )

* Add our new type definitions to the extension

.. code-block:: python

    new_data_types = [labmetadata_ext]

**4.** Generate the schema for the extension by running the ``create_extension_spec.py`` script

.. code-block:: bash

   cd ndx-labmetadata-example
   python src/spec/create_extension_spec.py

**5.** Edit  ``src/pynwb/__init__.py`` to define Python API classes for our new extension data types via :py:meth:`pynwb.get_class`.

.. code-block:: python

    LabMetaDataExtensionExample = get_class('LabMetaDataExtensionExample', 'ndx-labmetadata-example')

**6.** Define unit tests for the extension. The :nwb_extension_git:`ndx-template` created an example test
module ``src/pynwb/tests/test_tetrodeseries.py`` to illustrate how to implement tests. Here we simply remove
this file and replace it with our own tests `test_labmetadata_example.py <https://github.com/NeurodataWithoutBorders/ndx-labmetadata-example/blob/dev/src/pynwb/tests/test_labmetadata_example.py>`_. More details below in :ref:`extension-example-labmetadata-unittest`.

**7.** To make sure our extension schema and source code files are version controlled, we now add all the files we just created to the Git repo:

.. code-block:: bash

    git add .
    git commit -m "Added API classes, tests, and schema files"


**8.** Install your extension (Python only)(Optional)

.. code-block:: bash

   pip install .

Now our extension is ready to use!


Creating custom Python API classes
""""""""""""""""""""""""""""""""""

We skip this step here, since this extension of :py:class:`~pynwb.file.LabMetaData` is simple enough that the 
autogenerated class is sufficient. If the autogenerated class from :py:meth:`pynwb.get_class` for an extension
data types is not sufficient, then we can either customize the autogenerated class as described in
:ref:`extension-auto-pythonapi` (recommended only for basic changes) or define our own custom API class as
described in :ref:`extension-custom-api` (recommended for full customization).


.. _extension-example-labmetadata-unittest:

Creating unit tests
"""""""""""""""""""

.. tabs::

    .. tab:: Python

      .. tabs::

        .. code-tab:: py Unit test

            from pynwb.testing.mock.file import mock_NWBFile
            from pynwb.testing import TestCase
            from ndx_labmetadata_example import LabMetaDataExtensionExample


            class TestLabMetaDataExtensionExample(TestCase):
                """Test basic functionality of LabMetaDataExtensionExample without read/write"""

                def setUp(self):
                    """Set up an NWB file. Necessary because TetrodeSeries requires references to electrodes."""
                    self.nwbfile = mock_NWBFile()

                def test_constructor(self):
                    """Test that the constructor for TetrodeSeries sets values as expected."""
                    tissue_preparation = "Example tissue preparation"
                    lmdee_object = LabMetaDataExtensionExample(tissue_preparation=tissue_preparation)
                    self.assertEqual(lmdee_object.tissue_preparation, tissue_preparation)

        .. code-tab:: py Roundtrip test  (read/write)

            from pynwb.testing.mock.file import mock_NWBFile
            from pynwb.testing import TestCase
            from pynwb.testing.testh5io import NWBH5IOMixin
            from ndx_labmetadata_example import LabMetaDataExtensionExample

            class TestLabMetaDataExtensionExampleRoundtrip(NWBH5IOMixin, TestCase):
                """
                Roundtrip test for LabMetaDataExtensionExample to test read/write

                This test class writes the LabMetaDataExtensionExample to an NWBFile, then
                reads the data back from the file, and compares that the data read from file
                is consistent with the original data. Using the pynwb.testing infrastructure
                simplifies this complex test greatly by allowing to simply define how to
                create the container, add to a file, and retrieve it form a file. The
                task of writing, reading, and comparing the data is then taken care of
                automatically by the NWBH5IOMixin.
                """

                def setUpContainer(self):
                    """set up example LabMetaDataExtensionExample object"""
                    self.lab_meta_data = LabMetaDataExtensionExample(tissue_preparation="Example tissue preparation")
                    return self.lab_meta_data

                def addContainer(self, nwbfile):
                    """Add the test LabMetaDataExtensionExample to the given NWBFile."""
                    nwbfile.add_lab_meta_data(lab_meta_data=self.lab_meta_data)

                def getContainer(self, nwbfile):
                    """Get the LabMetaDataExtensionExample object from the given NWBFile."""
                    return nwbfile.get_lab_meta_data(self.lab_meta_data.name)


        .. code-tab:: bash Running Python unit tests

                cd ndx-labmetadata-example
                pytest

    .. tab:: MATLAB

        .. tabs::

            .. code-tab:: c Unit test

                Coming soon ...

            .. code-tab:: c Roundtrip test  (read/write)

                Coming soon ...

            .. code-tab:: bash Running MATLAB unit tests

                Coming soon ...


Documenting the extension
"""""""""""""""""""""""""

* **REAME.md:** Add instructions to the ``README.md`` file. This typically includes information on how to install the
  extension and an example on how to use the extension
* **Schema and user documentation:**

    * Install the latest release of hdmf_docutils: ``python -m pip install hdmf-docutils``
    * Generate the documentation for your extension based on the YAML schema files via:

    .. code-block:: bash

        cd docs/
        make html

    * To view the docs, simply open ``docs/build/html/index.html`` in your browser
    * See the `docs/README.md <https://github.com/NeurodataWithoutBorders/ndx-labmetadata-example/blob/dev/docs/README.md>`_
      for instructions on how to customize the documentation for your extension.

See :ref:`extension-documentation` for more details.

Writing data using the extension
""""""""""""""""""""""""""""""""

.. tabs::

   .. code-tab:: py Python

        from pynwb.file import NWBFile, Subject
        from ndx_labmetadata_example import LabMetaDataExtensionExample
        from pynwb import NWBHDF5IO
        from uuid import uuid4
        from datetime import datetime

        # create an example NWBFile
        nwbfile = NWBFile(
            session_description="test session description",
            identifier=str(uuid4()),
            session_start_time=datetime(1970, 1, 1),
            subject=Subject(
                age="P50D",
                description="example mouse",
                sex="F",
                subject_id="test_id")
        )

        # create our custom lab metadata
        lab_meta_data = LabMetaDataExtensionExample(tissue_preparation="Example tissue preparation")

        # Add the test LabMetaDataExtensionExample to the NWBFile
        nwbfile.add_lab_meta_data(lab_meta_data=lab_meta_data)

        # Write the file to disk
        filename = "testfile.nwb"
        with NWBHDF5IO(path=filename, mode="a") as io:
            io.write(nwbfile)

   .. code-tab:: c MATLAB

      Coming soon ...


Reading an NWB file that uses the extension
"""""""""""""""""""""""""""""""""""""""""""

.. tabs::

    .. code-tab:: py Python

        from pynwb import NWBHDF5IO
        from ndx_labmetadata_example import LabMetaDataExtensionExample

        # Read the file from disk
        io =  NWBHDF5IO(path=filename, mode="r")
        nwbfile = io.read()
        # Get the custom lab metadata object
        lab_meta_data = nwbfile.get_lab_meta_data(name="custom_lab_metadata")

    .. code-tab:: py Python (without extension installed)

        from pynwb import NWBHDF5IO

        # Read the file from disk. Load the namespace from file to
        # autogenerate classes from the schema
        io =  NWBHDF5IO(path=filename, mode="r", load_namespaces=True)
        nwbfile = io.read()
        # Get the custom lab metadata object
        lab_meta_data = nwbfile.get_lab_meta_data(name="custom_lab_metadata")

    .. code-tab:: c MATLAB

        Coming soon ...



Publishing the extension
"""""""""""""""""""""""""

The steps to publish an extension are the same for all extensions. We, therefore, here only briefly describe
he main steps for publishing our extension. For a more in-depth guide, see the page :ref:`extension-publishing`

* **GitHub (Open Source):** To make the sources of your extension openly accessible, publish the extension
  on GitHub by following the instructions on :ref:`extension-publishing-github`.

* **PyPI (Open Access):** Publish your extension on `PyPI <https://pypi.org>`_ to make it easy for users to 
  install it and to create a persistent release of the extension following the :ref:`extension-publishing-pypi` guide.

* **NDX Catalog (Open Publication)**: The :ndx-catalog:`NDX Catalog <>` serves as a central, community-led catalog
  for extensions to the NWB data standard. The NDX Catalog manages basic metadata about extensions while ownership
  of the source repositories for the extensions remain with the developers. For a step-by-step guide the
  :ref:`extension-publishing-ndxcatalog` guide.


