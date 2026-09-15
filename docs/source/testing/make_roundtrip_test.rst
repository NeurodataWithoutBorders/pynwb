=============================
How to Make a Roundtrip  Test
=============================

The PyNWB test suite has tools for easily doing round-trip tests of container classes. These
tools exist in the integration test suite in ``tests/integration/ui_write/base.py`` for this reason
and for the sake of keeping the repository organized, we recommend you write your tests in
the ``tests/integration/ui_write`` subdirectory of the Git repository.

For executing your new tests, we recommend using the `test.py` script in the top of the Git
repository. Roundtrip tests will get executed as part of the integration test suite, which can be executed
with the following command::

    $ python test.py -i

The roundtrip test will generate a new NWB file with the name ``test_<CLASS_NAME>.nwb`` where ``CLASS_NAME`` is
the class name of the :py:class:`~hdmf.container.Container` class you are roundtripping. The test
will write an NWB file with an instance of the container to disk, read this instance back in, and compare it
to the instance that was used for writing to disk. Once the test is complete, the NWB file will be deleted.
You can keep the NWB file around after the test completes by setting the environment variable ``CLEAN_NWB``
to ``0``, ``false``, ``False``, or ``FALSE``. Setting ``CLEAN_NWB`` to any value not listed here will
cause the roundtrip NWB file to be deleted once the test has completed

Before writing tests, we also suggest you familiarize yourself with the
:ref:`software architecture <software-architecture>` of PyNWB.

-----------------
``NWBH5IOMixin``
-----------------

To write a roundtrip test, you will need to subclass the :py:class:`~pynwb.testing.testh5io.NWBH5IOMixin` class and
override some of its instance methods.

:py:class:`~pynwb.testing.testh5io.NWBH5IOMixin` provides four methods for testing the process of going from
in-memory Python object to data stored on disk and back. Three of these methods--``setUpContainer``,
``addContainer``, and ``getContainer``--are required for carrying out the roundtrip test. The fourth method is
required for testing the conversion from the container to the :py:mod:`builder <hdmf.build.builders>`--the
intermediate data structure that gets used by :py:class:`~hdmf.backends.io.HDMFIO` implementations for writing to disk.

If you do not want to test step of the process, you can just implement ``setUpContainer``, ``addContainer``, and
``getContainer``.

##################
``setUpContainer``
##################

The first thing (and possibly the *only* thing -- see :ref:`rt_below`) you need to do is override is the ``setUpContainer``
method. This method should take no arguments, and return an instance of the container class you are testing.

Here is an example using a generic :py:class:`~pynwb.base.TimeSeries`:

.. code-block:: python

    from pynwb.testing import NWBH5IOMixin, TestCase


    class TimeSeriesRoundTrip(NWBH5IOMixin, TestCase):

        def setUpContainer(self):
            return TimeSeries(
                "test_timeseries",
                "example_source",
                list(range(100, 200, 10)),
                "SIunit",
                timestamps=list(range(10)),
                resolution=0.1,
            )


################
``addContainer``
################

The next thing is to tell the :py:class:`~pynwb.testing.testh5io.NWBH5IOMixin` how to add the container to an NWBFile.
This method takes a single argument--the :py:class:`~pynwb.file.NWBFile` instance that will be used to write your
container.

This method is required because different container types are allowed in different parts of an NWBFile. This method is
also where you can add additional containers that your container of interest depends on. For example, for the
:py:class:`~pynwb.ecephys.ElectricalSeries` roundtrip test, ``addContainer`` handles adding the
:py:class:`~pynwb.ecephys.ElectrodeGroup`, :py:class:`~pynwb.file.ElectrodeTable`, and
:py:class:`~pynwb.device.Device` dependencies.


Continuing from our example above, we will add the method for adding a generic :py:class:`~pynwb.base.TimeSeries` instance:


.. code-block:: python

    class TimeSeriesRoundTrip(NWBH5IOMixin, TestCase):

        def addContainer(self, nwbfile):
            nwbfile.add_acquisition(self.container)


################
``getContainer``
################

Finally, you need to tell :py:class:`~pynwb.testing.testh5io.NWBH5IOMixin` how to get back the container we added. As
with ``addContainer``, this method takes an :py:class:`~pynwb.file.NWBFile` as its single argument. The only
difference is that this :py:class:`~pynwb.file.NWBFile` instance is what was read back in.

Again, since not all containers go in the same place, we need to tell the test harness how to get back our container
of interest.

To finish off example from above, we will add the method for getting back our generic :py:class:`~pynwb.base.TimeSeries` instance:

.. code-block:: python

    class TimeSeriesRoundTrip(NWBH5IOMixin, TestCase):

        def getContainer(self, nwbfile):
            return nwbfile.get_acquisition(self.container.name)


################
``setUpBuilder``
################

As mentioned above, there is an optional method to override. This method will add two additional tests. First, it will
add a test for converting your container into a builder to make sure the intermerdiate data structure gets built
appropriately. Second it will add a test for constructing your container from the builder returned by your overridden
``setUpBuilder`` method.  This method takes no arguments, and should return the builder representation of your
container class instance.


This method is not required, but can serve as an additional check to make sure your containers are getting converted
to the expected structure as described in your specification.

Continuing from the :py:class:`~pynwb.base.TimeSeries` example, lets add ``setUpBuilder``:

.. code-block:: python

    from hdmf.build import GroupBuilder

    class TimeSeriesRoundTrip(NWBH5IOMixin, TestCase):

        def setUpBuilder(self):
            return GroupBuilder(
                'test_timeseries',
                attributes={
                    'source': 'example_source',
                    'namespace': base.CORE_NAMESPACE,
                    'neurodata_type': 'TimeSeries',
                    'description': 'no description',
                    'comments': 'no comments',
                },
                datasets={
                    'data': DatasetBuilder(
                        'data', list(range(100, 200, 10)),
                        attributes={
                            'unit': 'SIunit',
                            'conversion': 1.0,
                            'resolution': 0.1,
                        }
                    ),
                    'timestamps': DatasetBuilder(
                        'timestamps', list(range(10)),
                        attributes={'unit': 'Seconds', 'interval': 1},
                    )
                }
            )

.. _rt_below:

------------------------
``AcquisitionH5IOMixin``
------------------------

If you are testing something that can go in *acquisition*, you can avoid writing ``addContainer`` and ``getContainer``
by extending :py:class:`~pynwb.testing.testh5io.AcquisitionH5IOMixin`.  This class has already overridden these
methods to add your container object to acquisition.

Even if your container can go in acquisition, you may still need to override ``addContainer`` if your container depends
other containers that you need to add to the :py:class:`~pynwb.file.NWBFile` that will be written.
