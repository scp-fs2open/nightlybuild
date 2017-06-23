import requests
import re

from files import ReleaseFile


def get_release_files(tag_name, config):
    def execute_request(path):
        headers = {
            "Accept": "application/vnd.github.v3+json"
        }
        url = "https://api.github.com" + path

        response = requests.get(url, headers=headers)

        response.raise_for_status()

        return response.json()

    build_group_regex = re.compile("fs2_open_.*-builds-([^.-]*)(-([^.]*))?.*")

    response = execute_request(
        "/repos/{}/{}/releases/tags/{}".format(config["github"]["user"], config["github"]["repo"], tag_name))

    tarball = response["tarball_url"]
    out_data = []
    for asset in response["assets"]:
        url = asset["browser_download_url"]
        name = asset["name"]

        group_match = build_group_regex.match(name)

        out_data.append(ReleaseFile(name, url, group_match.group(1), group_match.group(3), tarball))

    return out_data
