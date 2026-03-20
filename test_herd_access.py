"""Test how external_resources can be accessed on NWBFile."""
from datetime import datetime
from uuid import uuid4

from dateutil import tz

from pynwb import NWBFile
from pynwb.resources import HERD

session_start_time = datetime(2018, 4, 25, 2, 30, 3, tzinfo=tz.gettz("US/Pacific"))
herd = HERD()
nwbfile = NWBFile(
    session_description="test",
    identifier=str(uuid4()),
    session_start_time=session_start_time,
    external_resources=herd,
)

# Try various ways to access external_resources
attrs_to_try = [
    "external_resources",
    "_external_resources",
    "_linked_external_resources",
    "general_external_resources",
    "general__external_resources",
    "fields",
]

for attr in attrs_to_try:
    val = getattr(nwbfile, attr, "NOT FOUND")
    print(f"nwbfile.{attr}: {val}")

print()

# Check if external_resources shows up in fields
print("nwbfile.fields:", nwbfile.fields)
print()

# Check children
for child in nwbfile.children:
    if "external" in type(child).__name__.lower() or "herd" in type(child).__name__.lower():
        print(f"Found in children: {child} (type={type(child).__name__})")

# Check if the HERD is the same object
print()
print(f"nwbfile.external_resources is herd: {nwbfile.external_resources is herd}")
print(f"nwbfile._external_resources is herd: {nwbfile._external_resources is herd}")
