Documenting Extensions
----------------------

Using the same tools used to generate the documentation for the `NWB-N core format <https://nwb-schema.readthedocs.io/en/latest/>`_
one can easily generate documentation in HTML, PDF, ePub and many other format for extensions as well.

Code to generate this documentation is maintained in a separate repo: https://github.com/hdmf-dev/hdmf-docutils. To use these utilities, install the package with pip:

.. code-block:: text

    pip install hdmf-docutils

For the purpose of this example, we assume that our current directory has the following structure.


.. code-block:: text

    - my_extension/
      - my_extension_source/
          - mylab.namespace.yaml
          - mylab.specs.yaml
          - ...
          - docs/  (Optional)
              - mylab_description.rst
              - mylab_release_notes.rst

In addition to Python 3.x, you will also need ``sphinx`` (including the ``sphinx-quickstart`` tool) installed.
Sphinx is available here http://www.sphinx-doc.org/en/stable/install.html .

We can now create the sources of our documentation as follows:

.. code-block:: text

    python3 nwb_init_sphinx_extension_doc  \
                 --project test \
                 --author "Dr. Master Expert" \
                 --version "1.2.3" \
                 --release alpha \
                 --output my_extension_docs \
                 --spec_dir my_extension_source \
                 --namespace_filename mylab.namespace.yaml \
                 --default_namespace mylab
                 --external_description my_extension_source/docs/mylab_description.rst \  (Optional)
                 --external_release_notes my_extension_source/docs/mylab_release_notes.rst \  (Optional)

To automatically generate the RST documentation files from the YAML (or JSON) sources of the extension simply run:

.. code-block:: text

    cd my_extension_docs
    make apidoc

Finally, to generate the HTML version of the docs run:

.. code-block:: text

    make html

.. tip::

    Additional instructions for how to use and customize the extension documentations are also available
    in the ``Readme.md`` file that  ``init_sphinx_extension_doc.py`` automatically adds to the docs.

.. tip::

    See ``make help`` for a list of available options for building the documentation in many different
    output formats (e.g., PDF, ePub, LaTeX, etc.).

.. tip::

    See ``python3 init_sphinx_extension_doc.py --help`` for a complete list of option to customize the documentation
    directly during initialization.

.. tip::

    The above example included additional description and release note docs as part of the specification. These are
    included in the docs via ``.. include`` commands so that changes in those files are automatically picked up
    when rebuilding to docs. Alternatively, we can also add custom documentation directly to the docs.
    In this case the options ``--custom_description format_description.rst``
    and ``--custom_release_notes format_release_notes.rst`` of the ``init_sphinx_extension_doc.py`` script are useful
    to automatically generate the basic setup for those files so that one can easily start to add content directly
    without having to worry about the additional setup.