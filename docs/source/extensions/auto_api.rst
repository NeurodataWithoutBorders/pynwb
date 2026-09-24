.. _extension-auto-api:

Generating an API for an extension
------------------------------------

.. _extension-auto-matlabnapi:

Generating a MatNWB API
~~~~~~~~~~~~~~~~~~~~~~~

In MatNWB, simply call ``generateExtension("path/to/extension/namespace.yaml");``; The class files will be generated under the ``+types/+<extension>`` module and can be accessed via standard MATLAB class semantics:

.. code-block:: MATLAB

    ts = types.ndx_example.TetrodeSeries(<arguments>);

.. note::
    As seen above, MatNWB will convert namespace names if they are not valid identifiers in MATLAB. See `Variable Names <https://www.mathworks.com/help/matlab/matlab_prog/variable-names.html>`_ for more information. In most cases, the conversion conforms with MATLAB's approach with `matlab.lang.makeValidName() <https://www.mathworks.com/help/matlab/ref/matlab.lang.makevalidname.html>`_

.. _extension-auto-pythonapi:

Generating a PyNWB API
~~~~~~~~~~~~~~~~~~~~~~

Now that we have created the extension specification, we need to create the Python interface. These classes will be
used just like the PyNWB API to read and write NWB files using Python. There are two ways to do this: you can
automatically generate the API classes based on the schema, or you can manually create the API classes. Here, we will
show you how to automatically generate the API. In the next section we will discuss why and how to create custom API
classes.


Open up ``ndx-example/src/pynwb/ndx_example/__init__.py``, and notice the last line:

.. code-block:: python

    TetrodeSeries = get_class('TetrodeSeries', 'ndx-example')

:py:func:`~pynwb.get_class` is a function that automatically creates a Python API object by parsing the extension
YAML. If you create more neurodata types, simply go down the line creating each one. This is the same object that is
created when you use the ``load_namespaces`` flag on :py:func:`~pynwb.NWBHDF5IO.__init__`.

Customizing automatically generated APIs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Once these classes are generated, you can customize them by dynamically adding or replacing attributes/methods (a.k.a., monkey patching).

A typical example is adding methods. Let's say you wanted a method that could
return data from only the first channel. You could add that method like this:

.. code-block:: python

    def data_from_first_chan(self):
        return self.data[:, 0]

    TetrodeSeries.data_from_first_chan = data_from_first_chan

You can also alter existing methods by overwriting them. Lets suppose you wanted to ensure that the
``trode_id`` field is never less than 0 for the ``TetrodeSeries`` constructor. You can do this by creating a new
``__init__`` function and assigning it to the class.

.. code-block:: python

    from hdmf.utils import docval, get_docval
    from hdmf.common.table import DynamicTableRegion

    @docval(get_docval(TetrodeSeries.__init__))
    def new_init(self, **kwargs):
        assert kwargs['trode_id'] >=0, f"`trode_id` must be greater than or equal to 0."
        TetrodeSeries.__init__(self, **kwargs)

    TetrodeSeries.__init__ = new_init

The above code creates a ``new_init`` method that runs a validation step and then calls the original ``__init__``.
Then the class ``__init__`` is overwritten by the new method. Here we also use ``docval``, which is described in the
next section.


.. tip::
    This approach is easy, but note your API will be locked to your specification. If you make changes to your
    specification there will be corresponding changes to the API, and this is likely to break existing code.
    Also, monkey patches can be very confusing to someone who is not aware of them. Differences
    between the installed module and the actual behavior of the source code can lead to frustrated
    developers. As such, this approach should be used with great care. In the
    next section we will show you how to create your own custom API that is more robust. In the
    :ref:`extension-custom-api` section, we'll explore how to build a fully customized API.
