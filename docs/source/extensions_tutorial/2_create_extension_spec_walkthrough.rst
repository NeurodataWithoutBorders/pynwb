Creating an extension
=====================

Using ndx-template
~~~~~~~~~~~~~~~~~~
Extensions should be created in their own repository, not alongside data conversion code. This facilitates sharing
and editing of the extension separately from the code that uses it. When starting a new extension, we highly
recommend using the :nwb_extension:`ndx-template` repository, which automatically generates a repository with
the appropriate directory structure.

After you finish the instructions :nwb_extension:`here <ndx-template#getting-started>`,
you should have a directory structure that looks like this

.. code-block:: bash

    ├── LICENSE.txt
    ├── MANIFEST.in
    ├── NEXTSTEPS.md
    ├── README.md
    ├── docs
    │   ├── Makefile
    │   ├── README.md
    │   ├── make.bat
    │   └── source
    │       ├── _static
    │       │   └── theme_overrides.css
    │       ├── conf.py
    │       ├── conf_doc_autogen.py
    │       ├── credits.rst
    │       ├── description.rst
    │       ├── format.rst
    │       ├── index.rst
    │       └── release_notes.rst
    ├── requirements.txt
    ├── setup.cfg
    ├── setup.py
    ├── spec
    │   ├── ndx-example.extensions.yaml
    │   └── ndx-example.namespace.yaml
    └── src
        ├── matnwb
        │   └── README.md
        ├── pynwb
        │   ├── README.md
        │   ├── ndx_example
        │   │   └── __init__.py
        │   └── tests
        │       ├── __init__.py
        │       └── test_tetrodeseries.py
        └── spec
            └── create_extension_spec.py

At its core, an NWB extension consists of YAML text files, such as those generated in the `spec`
folder. While you can write these YAML extension files by hand, PyNWB provides a convenient API
via the :py:mod:`~pynwb.spec` module for creating extensions.

Open ``src/spec/create_extension_spec.py``. You will be
modifying this script to create your own NWB extension. Let's first walk through each piece.

Creating a namespace
~~~~~~~~~~~~~~~~~~~~
NWB organizes types into namespaces. You must define a new namespace before creating any new types. After following
the instructions from the :nwb_extension:`ndx-template`, you should have a file
``ndx-my-ext/src/spec/create_extension_spec.py``. The beginning of this file should look like

.. code-block:: python

    from pynwb.spec import NWBNamespaceBuilder, export_spec, NWBGroupSpec, NWBAttributeSpec
    # TODO: import the following spec classes as needed
    # from pynwb.spec import NWBDatasetSpec, NWBLinkSpec, NWBDtypeSpec, NWBRefSpec


    def main():
        # these arguments were auto-generated from your cookiecutter inputs
        ns_builder = NWBNamespaceBuilder(
            doc="my description",
            name="ndx-my-ext",
            version="0.1.0",
            author="John Doe",
            contact="contact@gmail.com"
        )

Here, after the initial imports, we are defining meta-data of the extension.
Pay particular attention to ``version``. If you make changes to your extension
after the initial release, you should increase the numbers in your version
number, so that you can keep track of what exact version of the extension was
used for each file. We recommend using a `semantic versioning approach <https://nwb-extensions.github.io/versioning_guidelines>`_.

Including types
~~~~~~~~~~~~~~~

Next, we need to include types from the core schemas. This is analogous to
importing classes in Python. The generated file includes some example imports.

.. code-block:: python

    ns_builder.include_type('ElectricalSeries', namespace='core')
    ns_builder.include_type('TimeSeries', namespace='core')
    ns_builder.include_type('NWBDataInterface', namespace='core')
    ns_builder.include_type('NWBContainer', namespace='core')
    ns_builder.include_type('DynamicTableRegion', namespace='hdmf-common')
    ns_builder.include_type('VectorData', namespace='hdmf-common')
    ns_builder.include_type('Data', namespace='hdmf-common')

Neuroscience-specific data types are defined in the namespace ``'core'``
(which means core NWB). More general organizational data types that are not
specific to neuroscience and are relevant across scientific fields are defined
in ``'hdmf-common'``. You can see which types are defined in which namespace by
exploring the `NWB schema documentation <https://nwb-schema.readthedocs.io/en/latest/>`_
and hdmf-common schema documentation <https://hdmf-common-schema.readthedocs.io/en/latest/>`_.

Defining new neurodata types
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Next, the ``create_extension_spec.py`` file declares an example extension
for a new neurodata type called ``TetrodeSeries``, which extends the :py:class:`~pynwb.ecephys.ElectricalSeries`
type. Then it creates a list of all new data types.

.. code-block:: python

    tetrode_series = NWBGroupSpec(
        neurodata_type_def='TetrodeSeries',
        neurodata_type_inc='ElectricalSeries',
        doc=('An extension of ElectricalSeries to include the tetrode ID for '
             'each time series.'),
        attributes=[
            NWBAttributeSpec(
                name='trode_id',
                doc='The tetrode ID.',
                dtype='int32'
            )
        ],
    )

    # TODO: add all of your new data types to this list
    new_data_types = [tetrode_series]

The remainder of the file is to generate the YAML files from the spec definition, and should not be changed.

After you make changes to this file, you should run it to re-generate the ``ndx-[name].extensions.yaml`` and
``ndx-[name].namespace.yaml`` files. In the next section, we will go into more detail into how to create neurodata
types.
