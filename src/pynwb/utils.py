import re

from hdmf.build import Builder


def get_nwb_version(builder: Builder):
    """Get the version of the NWB file from the root of the given builder, as a tuple.

    If the "nwb_version" attribute on the root builder equals "2.5.1", then (2, 5, 1) is returned.
    If the "nwb_version" attribute on the root builder equals "2.5.1-alpha", then (2, 5, 1) is returned.
    """
    temp_builder = builder
    while temp_builder.parent is not None:
        temp_builder = temp_builder.parent
    root_builder = temp_builder
    nwb_version = root_builder.attributes.get("nwb_version")
    if nwb_version is None:
        raise ValueError("'nwb_version' attribute is missing from root of NWB file.")
    nwb_version = re.match("(\d+\.\d+\.\d+)", nwb_version)[0]  # trim off any non-numeric symbols at end
    return tuple([int(i) for i in nwb_version.split(".")])
