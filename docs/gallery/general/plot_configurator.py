"""
TypeConfigurator
=======

This is a user guide for how to take advantage of the
:py:class:`~hdmf.term_set.TypeConfigurator` class by creating configuration files in
order to more easily validate terms within datasets or attributes.

Introduction
-------------
Users do not directly interact with the :py:class:`~hdmf.term_set.TypeConfigurator` class.
Instead, users wil create a configuration YAML file that outlines the fields (within a neurodata type)
they want to be validated. After creating the configuration file, users will need to load the
configuration with the :py:func:`~pynwb.load_type_config` method.
With the configuration loaded, every instance of the neurodata
types defined in the configuration file will have the respective fields wrapped with a
:py:class:`~hdmf.term_set.TermSetWrapper`.
This automatic wrapping is what provides the term validation for the the field value.
If a user wants to have greater control on which instances have validated fields, the user cannot use the
configurator, bur rather proceed with manually wrapping with a
:py:class:`~hdmf.term_set.TermSetWrapper`.

To unload a configuration, simply call :py:func:`~pynwb.unload_type_config`.
We also provide a helper method to see the configuration that has been loaded:
:py:func:`~pynwb.get_loaded_type_config`


How to make a Configuration File
--------------------------------
Before taking advantage of the all the wonders that comes with using a configuration file,
the user needs to create one following some simple guidelines. To follow along with an example,
please refer to ``nwb_config.yaml`` under ``src/config``. 
The configuration files is built on the foundation of the YAML syntax. The
user will construct a series of nested dictioanries to encompass all the necessary information.

1. The user needs to define all the relevant namespaces. Recall that each neurodata type exists within
   a namespace, whether that is the core namespace in PyNWB or a namespace in an extension. As namespaces grow,
   we also require a version to be recorded in the configuration file to ensure proper functionality.
2. Within a namespace dictionary, the user will have a list of data types the want to use.
3. Each data type will have a list of fields associated with a :py:class:`~hdmf.term_set.TermSet`.
   The user can use the same or unique TermSet instances for each field.
"""
try:
    import linkml_runtime  # noqa: F401
except ImportError as e:
    raise ImportError("Please install linkml-runtime to run this example: pip install linkml-runtime") from e
from hdmf.term_set import TermSet, TermSetWrapper

# How to use a Configuration file
# -------------------------------
# As mentioned prior, the first step after creating a configuration file is
# to load the file.
# It is important to remember that with the configuration loaded, the fields
# are wrapped automatically, meaning the user should proceed with creating
# the instances normally, i.e., without wrapping directly. In this example,
# we load the the NWB curated configuration file that associates a
# :py:class:`~hdmf.term_set.TermSet` for the species field in Subject.
# The NWB configuration file is the default when you call
# :py:func:`~pynwb.load_type_config`.

load_type_config()

session_start_time = datetime(2018, 4, 25, hour=2, minute=30, second=3, tzinfo=tz.gettz("US/Pacific"))

nwbfile = NWBFile(
    session_description="Mouse exploring an open field",  # required
    identifier=str(uuid4()),  # required
    session_start_time=session_start_time,  # required
    session_id="session_1234",  # optional
    experimenter=[
        "Baggins, Bilbo",
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
subject

####################################
# How to see the Configuration file
# ---------------------------------
# Users can retrieve the loaded configuration.
config = get_loaded_type_config()

######################################
# How to unload the Configuration file
# ------------------------------------
# In order to toggle off the automatic validation, the user simple needs to unload
# the configuration.
unload_type_config()
