.. _export:

Exporting NWB files
===================

You can use the export feature of PyNWB to create a modified version of an existing NWB file, while preserving the
original file.

To do so, first open the NWB file using :py:class:`~pynwb.NWBHDF5IO`. Then, read the NWB file into an
:py:class:`~pynwb.file.NWBFile` object, modify the :py:class:`~pynwb.file.NWBFile` object or its child objects, and
export the modified :py:class:`~pynwb.file.NWBFile` object to a new file path. The modifications will appear in the
exported file and not the original file.

These modifications can consist of removals of containers, additions of containers, and changes to container attributes.
If container attributes are changed, then
:py:meth:`NWBFile.set_modified() <hdmf.container.AbstractContainer.set_modified>` must be called
on the :py:class:`~pynwb.file.NWBFile` before exporting.

.. code-block:: python

   with NWBHDF5IO(self.read_path, mode='r') as read_io:
       nwbfile = read_io.read()
       # ...  # modify nwbfile
       nwbfile.set_modified()  # this may be necessary if the modifications are changes to attributes

       with NWBHDF5IO(self.export_path, mode='w') as export_io:
           export_io.export(src_io=read_io, nwbfile=nwbfile)

.. note::

    Modifications to :py:class:`h5py.Dataset <h5py.Dataset>` objects act *directly* on the read file on disk.
    Changes are applied immediately and do not require exporting or writing the file. If you want to modify a dataset
    only in the new file, than you should replace the whole object with a new array holding the modified data. To
    prevent unintentional changes to the source file, the source file should be opened with ``mode='r'``.

.. note::

    Moving containers within the same file is currently not supported directly via export. See the following
    `discussion on the NWB Help Desk <https://github.com/NeurodataWithoutBorders/helpdesk/discussions/21>`_
    for details.

.. note::

    After exporting an :py:class:`~pynwb.file.NWBFile`, the object IDs of the :py:class:`~pynwb.file.NWBFile` and its
    child containers will be identical to the object IDs of the read :py:class:`~pynwb.file.NWBFile` and its child
    containers. The object ID of a container uniquely identifies the container within a file, but should *not* be
    used to distinguish between two different files.

.. seealso::

    The tutorial :ref:`modifying_data` provides additional examples of adding and removing containers from an NWB file.


How do I create a copy of an NWB file with different data layouts (e.g., applying compression)?
---------------------------------------------------------------------------------------------------------
Use the `h5repack <https://support.hdfgroup.org/HDF5/doc/RM/Tools.html#Tools-Repack>`_ command line tool from the HDF5 Group.
See also this `h5repack tutorial <https://support.hdfgroup.org/HDF5/Tutor/cmdtooledit.html#chglayout>`_.


How do I create a copy of an NWB file with different controls over how links are treated and whether copies are deep or shallow?
---------------------------------------------------------------------------------------------------------------------------------
Use the `h5copy <https://support.hdfgroup.org/HDF5/doc/RM/Tools.html#Tools-Copy>`_ command line tool from the HDF5 Group.
See also this `h5copy tutorial <https://support.hdfgroup.org/HDF5/Tutor/cmdtooledit.html#copy>`_.


How do I generate new object IDs for a newly exported NWB file?
---------------------------------------------------------------------------------------------------------
Before calling ``export``, call the method
:py:meth:`generate_new_id <hdmf.container.AbstractContainer.generate_new_id>` on the :py:class:`~pynwb.file.NWBFile`
to generate a new set of object IDs for the ``NWBFile`` and all of its children, recursively. Then export the
:py:class:`~pynwb.file.NWBFile`. The original NWB file is preserved.

.. code-block:: python

   with NWBHDF5IO(self.read_path, manager=manager, mode='r') as read_io:
       nwbfile = read_io.read()
       # ...  # modify nwbfile if desired
       nwbfile.generate_new_id()

       with NWBHDF5IO(self.export_path, mode='w') as export_io:
           export_io.export(src_io=read_io, nwbfile=nwbfile)


My NWB file contains links to datasets in other HDF5 files. How do I create a new NWB file with copies of the datasets?
-----------------------------------------------------------------------------------------------------------------------
Pass the keyword argument ``write_args={'link_data': False}`` to :py:meth:`NWBHDF5IO.export <pynwb.NWBHDF5IO.export>`.
This is similar to passing the keyword argument ``link_data=False`` to
:py:meth:`NWBHDF5IO.write <hdmf.backends.hdf5.h5tools.HDF5IO.write>` when writing a file with a
copy of externally linked datasets.

For example:

.. code-block:: python

   with NWBHDF5IO(self.read_path, mode='r') as read_io:
       nwbfile = read_io.read()
       # nwbfile contains a TimeSeries where the TimeSeries data array is a link to an external dataset
       # in a different HDF5 file than self.read_path

       with NWBHDF5IO(self.export_path, mode='w') as export_io:
           export_io.export(src_io=read_io, nwbfile=nwbfile, write_args={'link_data': False})  # copy linked datasets
           # the written file will contain no links to external datasets

You can also the `h5copy <https://support.hdfgroup.org/HDF5/doc/RM/Tools.html#Tools-Copy>`_ command line tool \
from the HDF5 Group. See also this `h5copy tutorial <https://support.hdfgroup.org/HDF5/Tutor/cmdtooledit.html#copy>`_.


How do I write a newly instantiated ``NWBFile`` to two different file paths?
-----------------------------------------------------------------------------------------------------------------------
PyNWB does not support writing an :py:class:`~pynwb.file.NWBFile` that was not read from a file to two different files.
For example, if you instantiate :py:class:`~pynwb.file.NWBFile` A and write it to file path 1, you cannot also write it
to file path 2. However, you can first write the :py:class:`~pynwb.file.NWBFile` to file path 1, read the
:py:class:`~pynwb.file.NWBFile` from file path 1, and then export it to file path 2.

.. code-block:: python

   with NWBHDF5IO(self.filepath1, manager=manager, mode='w') as write_io:
       write_io.write(nwbfile)

   with NWBHDF5IO(self.filepath1, manager=manager, mode='r') as read_io:
       read_nwbfile = read_io.read()

       with NWBHDF5IO(self.filepath2, mode='w') as export_io:
           export_io.export(src_io=read_io, nwbfile=nwbfile)
