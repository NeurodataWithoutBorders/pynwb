def _search_dandi_assets(url, filepath):
    import requests

    response = requests.request("GET", url, headers={"Accept": "application/json"}).json()

    for asset in response["results"]:
        if filepath == asset["path"]:
            return asset["asset_id"]

    if response.get("next", None):
        return _search_dandi_assets(response["next"], filepath)

    return None


def get_dandi_asset_id(dandiset_id, filepath):
    url = f"https://api.dandiarchive.org/api/dandisets/{dandiset_id}/versions/draft/assets/"
    asset_id = _search_dandi_assets(url, filepath)
    if asset_id is None:
        raise ValueError(f'path {filepath} not found in dandiset {dandiset_id}.')
    return asset_id


def get_dandi_s3_url(dandiset_id, filepath):
    """Get the s3 location for any NWB file on DANDI"""
    import requests

    asset_id = get_dandi_asset_id(dandiset_id, filepath)
    url = f"https://api.dandiarchive.org/api/dandisets/{dandiset_id}/versions/draft/assets/{asset_id}/download/"

    s3_url = requests.request(url=url, method='head').url
    if '?' in s3_url:
        return s3_url[:s3_url.index('?')]
    return s3_url
