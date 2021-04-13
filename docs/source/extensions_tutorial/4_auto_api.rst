Automatic Extension API
-----------------------

Now that we have created the extension specification, we need to create the Python interface. These classes will be
used just like the PyNWB API to create NWB files in Python. In Python, there are two ways to do this, you can
automatically generate the API classes based on the schema, or you can manually create the API classes. Here, we will
show you how to automatically generate the API.

.. note::
    In MatNWB there is only one method: automatically generating the API. Simply call
    ``generateExtension("path/to/extension.yaml")``;


Open up ``ndx-example/src/pynwb/ndx_example/__init__.py``, and notice the last line:

.. code-block:: python

    TetrodeSeries = get_class('TetrodeSeries', 'ndx-example')

:py:func:`~pynwb.get_class` is a function that automatically creates a Python API object by parsing the extension
YAML. If you create more neurodata types, simply go down the line creating each one.

Customizing automatically generated APIs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Once these classes are generated, you can customize them by adding methods. Let's say you wanted a method that could
return data from only the first channel. You could add that method like this:

.. code-block:: python

    def data_from_first_chan(self):
        return self.data[:, 0]

    TetrodeSeries.data_from_first_chan = data_from_first_chan

You can also alter existing methods by overwriting them. Hypothetically lets suppose you wanted to ensure that the
``trode_id`` field is never less than 0 for the ``TetrodeSeries`` constructor. You can do this by creating a new
``__init__`` function and assigning it to the class.

.. code-block:: python

    from hdmf import docval
    from hdmf.common.table import DynamicTableRegion

    @docval(*TetrodeSeries.__init__.__docval__['args'])
    def new_init(self, **kwargs):
        assert kwargs['trode_id'] >=0, f"`trode_id` must be greater than or equal to 0."
        TetrodeSeries.__init__(self, **kwargs)

    TetrodeSeries.__init__ = new_init

The above code creates a ``new_init`` method that runs a validation step and then calls the original ``__init__``.
Then the class ``__init__`` is overwritten by the new method.

.. tip::
    This method is easier, but note your API will be locked to your specification. If you make changes to your
    specification there will be corresponding changes to the API, and this is likely to break existing code. In the
    next section we will show you how to create your own custom API that is more robust.
