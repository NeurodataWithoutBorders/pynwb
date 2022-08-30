from uuid import uuid4
from datetime import datetime

from ...file import NWBFile, Subject
from .utils import name_generator


def mock_NWBFile(
    session_description='session_description',
    identifier=None,
    session_start_time=datetime(1970, 1, 1),
    **kwargs
):
    return NWBFile(
        session_description=session_description,
        identifier=identifier or uuid4(),
        session_start_time=session_start_time,
        **kwargs
    )


def mock_Subject(
    age="P50D",
    description="this is a mock mouse.",
    sex="F",
    subject_id=None,
):

    return Subject(
        age=age,
        description=description,
        sex=sex,
        subject_id=subject_id or name_generator("subject"),
    )
