from typing import Optional
from uuid import uuid4
from datetime import datetime
from dateutil.tz import tzlocal

from ...file import NWBFile, Subject
from .utils import name_generator


def mock_NWBFile(
    session_description: str = 'session_description',
    identifier: Optional[str] = None,
    session_start_time: datetime = datetime(1970, 1, 1, tzinfo=tzlocal()),
    **kwargs
):
    return NWBFile(
        session_description=session_description,
        identifier=identifier or str(uuid4()),
        session_start_time=session_start_time,
        **kwargs
    )


def mock_Subject(
    age: Optional[str] = "P50D",
    description: str = "this is a mock mouse.",
    sex: Optional[str] = "F",
    subject_id: Optional[str] = None,
    nwbfile: Optional[NWBFile] = None,
):

    subject = Subject(
        age=age,
        description=description,
        sex=sex,
        subject_id=subject_id or name_generator("subject"),
    )

    if nwbfile is not None:
        nwbfile.subject = subject

    return subject
