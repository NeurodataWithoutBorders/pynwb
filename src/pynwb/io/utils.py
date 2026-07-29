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


# A trailing UTC offset that carries a seconds component (e.g. "-05:50:36"). Such offsets are
# outside ISO 8601 and are rejected by dateutil (and by datetime.fromisoformat before Python
# 3.11), even though they appear in files written by other tools.
_SUBMINUTE_OFFSET_RE = re.compile(r"(?P<sign>[+-])(?P<hours>\d{2}):(?P<minutes>\d{2}):(?P<seconds>\d{2})$")


def parse_subminute_offset_date(datestr):
    """Parse an ISO 8601 datetime whose UTC offset carries a seconds component.

    Returns a timezone-aware ``datetime``, or ``None`` if ``datestr`` does not end in such an
    offset or the remainder is not a valid naive datetime. Works on all supported Python
    versions, since it parses the offset itself instead of relying on ``fromisoformat``.
    """
    match = _SUBMINUTE_OFFSET_RE.search(datestr)
    if match is None:
        return None
    try:
        base = datetime.datetime.fromisoformat(datestr[:match.start()])
    except ValueError:
        return None
    if base.tzinfo is not None:
        return None
    offset = datetime.timedelta(
        hours=int(match.group("hours")),
        minutes=int(match.group("minutes")),
        seconds=int(match.group("seconds")),
    )
    if match.group("sign") == "-":
        offset = -offset
    return base.replace(tzinfo=datetime.timezone(offset))


def parse_date(datestr, field_name):
    """Parse an ISO 8601 date string read from a file into a ``datetime``.

    ``dateutil`` is tried first (the historical behavior), then ``datetime.fromisoformat``,
    then a fallback for sub-minute UTC offsets (e.g. ``-05:50:36``) that both reject on older
    Python. If none succeed, raise a ``ValueError`` naming the field and the offending string.
    """
    try:
        return dateutil_parse(datestr)
    except (ValueError, OverflowError):
        pass
    try:
        return datetime.datetime.fromisoformat(datestr)
    except ValueError:
        pass
    parsed = parse_subminute_offset_date(datestr)
    if parsed is not None:
        return parsed
    raise ValueError("Could not parse %s value %r as a datetime." % (field_name, datestr))
