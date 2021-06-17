Documenting Extensions
----------------------

Using the same tools used to generate the documentation for the `NWB core format <https://nwb-schema.readthedocs.io/en/latest/>`_,
one can easily generate documentation in HTML, PDF, ePub and many other formats for extensions.

If you used ndx-template, then your repository is already pre-configured to automatically generate documentation for
your extension. The ``docs`` directory structure should look like this.

.. code-block:: text

    ndx-my-extension/
        docs/
            source/
                credits.rst
                description.rst
                release_notes.rst
                ...


To generate the HTML documentation files from the YAML (or JSON) sources of the extension, simply run:

.. code-block:: text

    cd docs/source
    make html

The generated documentation will be available in ``build/html``. To view, open ``build/html/index.html`` in your browser.
These pages contain diagrams of your extension. Note that there are several places where information needs to be
added. For instance, the Overview section says:

.. note::

    Add the description of your extension here

Within ``docs/source``, edit ``credits.rst``, ``description.rst``, and ``release_notes.rst``, then rerun ``make html``.

Now that you have created documentation for your extension, it is time to learn how to publish in the NDX catalog.

See published extensions and learn how to share your extension on the `NDX Catalog website <https://nwb-extensions.github.io/>`_.
