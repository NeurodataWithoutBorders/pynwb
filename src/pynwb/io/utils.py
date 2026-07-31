import datetime
import re
from typing import Tuple

from dateutil.parser import parse as dateutil_parse
from hdmf.build import Builder, ObjectMapper

# Value an override function returns to signal "no override". HDMF >= 6.2.0 provides the
# ObjectMapper.NO_OVERRIDE sentinel; older HDMF uses a None return. getattr resolves to whichever
# the installed HDMF supports.
# TODO: return ObjectMapper.NO_OVERRIDE directly and remove this shim once the minimum required HDMF
# version is >= 6.2.0.
NO_OVERRIDE = getattr(ObjectMapper, "NO_OVERRIDE", None)


def get_nwb_version(builder: Builder, include_prerelease=False) -> Tuple[int, ...]:
    """Get the version of the NWB file from the root of the given builder, as a tuple.

    If the "nwb_version" attribute on the root builder equals "2.5.1", then (2, 5, 1) is returned.
    If the "nwb_version" attribute on the root builder equals "2.5.1-alpha" and include_prerelease=False,
    then (2, 5, 1) is returned.
    If the "nwb_version" attribute on the root builder equals "2.5.1-alpha" and include_prerelease=True,
    then (2, 5, 1, "alpha") is returned.

    If the "nwb_version" attribute == "2.0b" (the only deviation from semantic versioning in the 2.x series), then
    if include_prerelease=True, (2, 0, 0, "b") is returned; else, (2, 0, 0) is returned.

    :param builder: Any builder within an NWB file.
    :type builder: :py:class:`~hdmf.build.builders.Builder`
    :param include_prerelease: Whether to include prerelease information in the returned tuple.
    :type include_prerelease: bool
    :return: The version of the NWB file, as a tuple.
    :rtype: tuple
    :raises ValueError: if the 'nwb_version' attribute is missing from the root of the NWB file.
    """
    temp_builder = builder
    while temp_builder.parent is not None:
        temp_builder = temp_builder.parent
    root_builder = temp_builder
    nwb_version = root_builder.attributes.get("nwb_version")
    if nwb_version is None:
        raise ValueError("'nwb_version' attribute is missing from the root of the NWB file.")
    # handle special non-semver case
    if nwb_version == "2.0b":
        if not include_prerelease:
            return (2, 0, 0)
        else:
            return (2, 0, 0, "b")

    nwb_version = nwb_version.removeprefix("NWB-")
    nwb_version_match = re.match(r"(\d+\.\d+\.\d+)", nwb_version)[0]  # trim off any non-numeric symbols at end
    version_list = [int(i) for i in nwb_version_match.split(".")]
    if include_prerelease:
        prerelease_info = nwb_version[nwb_version.index("-")+1:]
        version_list.append(prerelease_info)
    return tuple(version_list)


def parse_date(datestr, field_name):
    """Parse an ISO 8601 date string read from a file into a ``datetime``.

    ``datestr`` may be ``str`` or UTF-8 ``bytes``. Scalar datasets are decoded on read, while
    elements of an array-valued dataset (``file_create_date``) carry whichever the file stores:
    a variable-length ``str`` dataset is decoded, a variable-length ``bytes`` one is not.

    ``dateutil`` handles the common formats. ``datetime.fromisoformat`` covers UTC offsets that
    carry a seconds component (e.g. ``-05:50:36``), which some writers emit. A value that neither
    accepts raises a ``ValueError`` naming the field and the offending string.
    """
    if isinstance(datestr, bytes):
        datestr = datestr.decode("utf-8")
    try:
        return dateutil_parse(datestr)
    except (ValueError, OverflowError) as err:
        parse_error = err
    try:
        return datetime.datetime.fromisoformat(datestr)
    except ValueError:
        pass
    raise ValueError(f"Could not parse {field_name} value {datestr!r} as a datetime.") from parse_error
