import pytest
from datetime import datetime
from dateutil.tz import tzutc


from ...file import NWBFile, Subject


@pytest.fixture()
def nwbfile():
    start = datetime(2017, 5, 1, 12, 0, 0, tzinfo=tzutc())
    ref_time = datetime(1979, 1, 1, 0, tzinfo=tzutc())
    create = [
        datetime(2017, 5, 1, 12,  tzinfo=tzutc()),
        datetime(2017, 5, 2, 13, 0, 0, 1, tzinfo=tzutc()),
        datetime(2017, 5, 2, 14, tzinfo=tzutc())
    ]
    return NWBFile(
        'a test session description for a test NWBFile',
        'FILE123',
        start,
        file_create_date=create,
        timestamps_reference_time=ref_time,
        experimenter='A test experimenter',
        lab='a test lab',
        institution='a test institution',
        experiment_description='a test experiment description',
        session_id='test1',
        notes='my notes',
        pharmacology='drugs',
        protocol='protocol',
        related_publications='my pubs',
        slices='my slices',
        surgery='surgery',
        virus='a virus',
        source_script='noscript',
        source_script_file_name='nofilename',
        stimulus_notes='test stimulus notes',
        data_collection='test data collection notes',
        keywords=('these', 'are', 'keywords')
    )


@pytest.fixture()
def subject():
    return Subject(
        age='12 mo',
        description='An unfortunate rat',
        genotype='WT',
        sex='M',
        species='Rattus norvegicus',
        subject_id='RAT123',
        weight='2 lbs',
        date_of_birth=datetime(2017, 5, 1, 12, tzinfo=tzutc())
    )
