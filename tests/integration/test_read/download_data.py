import requests
import os


def download_if_does_not_exist(filename, url):
    """
    Download an URL to a file
    """
    if not os.path.exists(filename):
        with open(filename, 'wb') as fout:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            for block in response.iter_content(4096):
                fout.write(block)


def download_test_data():
    data_dir = os.path.join('tests', 'integration', 'test_read', 'data')
    download_if_does_not_exist(
        os.path.join(data_dir, 'ophys_example.nwb'),
        'https://data.kitware.com/api/v1/file/5ab3e3398d777f068578ed1d/download')
