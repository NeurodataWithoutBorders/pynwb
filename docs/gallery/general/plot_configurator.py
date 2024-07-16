"""
How to Configure Term Validations
=================================

This is a user guide for how to curate and take advantage of configuration files in
order to more easily validate terms within datasets or attributes.

Introduction
-------------
Users will create a configuration YAML file that outlines the fields (within a neurodata type)
they want to be validated against a set of allowed terms. 
After creating the configuration file, users will need to load the
configuration file with the :py:func:`~pynwb.load_type_config` method.
With the configuration loaded, every instance of the neurodata
types defined in the configuration file will have the respective fields wrapped with a
:py:class:`~hdmf.term_set.TermSetWrapper`.
This automatic wrapping is what provides the term validation for the field value.
For greater control on which datasets and attributes are validated
against which sets of allowed terms, use the 
:py:class:`~hdmf.term_set.TermSetWrapper` on individual datasets and attributes instead.
You can follow the 
`TermSet tutorial in the HDMF documentation 
<https://hdmf.readthedocs.io/en/stable/tutorials/plot_term_set.html#sphx-glr-tutorials-plot-term-set-py>`_
for more information.

To unload a configuration, simply call :py:func:`~pynwb.unload_type_config`.
We also provide a helper method to see the configuration that has been loaded:
:py:func:`~pynwb.get_loaded_type_config`


How to make a Configuration File
--------------------------------
To see an example of a configuration file, please refer to
`<https://github.com/NeurodataWithoutBorders/pynwb/tree/dev/src/pynwb/config/nwb_config.yaml>`_.
The configuration file uses YAML syntax. The
user will construct a series of nested dictionaries to encompass all the necessary information.

1. The user needs to define all the relevant namespaces. Recall that each neurodata type exists within
   a namespace, whether that is the core namespace in PyNWB or a namespace in an extension. As namespaces grow,
   we also require a version to be recorded in the configuration file to ensure proper functionality.
2. Within a namespace dictionary, the user will have a list of data types they want to configure.
3. Each data type will have a list of fields associated with a :py:class:`~hdmf.term_set.TermSet`.
   The user can use the same or unique TermSet instances for each field.
"""
try:
    import linkml_runtime  # noqa: F401
except ImportError as e:
    raise ImportError("Please install linkml-runtime to run this example: pip install linkml-runtime") from e

from dateutil import tz
from datetime import datetime
from uuid import uuid4
import os

from pynwb import NWBFile, get_loaded_type_config, load_type_config, unload_type_config
from pynwb.file import Subject

####################################
# How to use a Configuration file
# -------------------------------
# As mentioned prior, the first step after creating a configuration file is
# to load the file. In this configuration file, we have defined two fields
# we want to always be validated: ``experimenter`` and ``species``. Each of these
# are from a different neurodata type, :py:class:`~pynwb.file.NWBFile` and
# :py:class:`~pynwb.file.Subject` respectively, and each
# have a unique associated :py:class:`~hdmf.term_set.TermSet`.
# It is important to remember that with the configuration loaded, the fields
# are wrapped automatically, meaning the user should proceed with creating
# the instances normally, i.e., without wrapping directly. Once instantiated,
# the value of the fields are wrapped and then validated to see if it is a
# permissible value in their respective :py:class:`~hdmf.term_set.TermSet`.

try:
    dir_path = os.path.dirname(os.path.abspath(__file__))  # when running as a .py
except NameError:
    dir_path = os.path.dirname(os.path.abspath("__file__"))  # when running as a script or notebook
yaml_file = os.path.join(dir_path, 'nwb_gallery_config.yaml')
load_type_config(config_path=yaml_file)

session_start_time = datetime(2018, 4, 25, hour=2, minute=30, second=3, tzinfo=tz.gettz("US/Pacific"))

nwbfile = NWBFile(
    session_description="Mouse exploring an open field",  # required
    identifier=str(uuid4()),  # required
    session_start_time=session_start_time,  # required
    session_id="session_1234",  # optional
    experimenter=[
        "Bilbo Baggins",
    ],  # optional
    lab="Bag End Laboratory",  # optional
    institution="University of My Institution",  # optional
    experiment_description="I went on an adventure to reclaim vast treasures.",  # optional
    related_publications="DOI:10.1016/j.neuron.2016.12.011",  # optional
)

subject = Subject(
    subject_id="001",
    age="P90D",
    description="mouse 5",
    species="Mus musculus",
    sex="M",
)

nwbfile.subject = subject

####################################
# How to see the Configuration file
# ---------------------------------
# Call :py:class:`~pynwb.get_loaded_type_config` to get a dictionary containing the
# current configuration.
config = get_loaded_type_config()

######################################
# How to unload the Configuration file
# ------------------------------------
# Call :py:class:`~pynwb.unload_type_config` to toggle off the automatic validation.
unload_type_config()
