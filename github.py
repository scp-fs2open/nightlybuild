from typing import List, Tuple, Dict

import requests
import re

from files import ReleaseFile
from files import SourceFile


def get_release_files(tag_name, config) -> Tuple[List[ReleaseFile], Dict[str, SourceFile]]:
    def execute_request(path):
        headers = {
            "Accept": "application/vnd.github.v3+json"
        }
        url = "https://api.github.com" + path

        response = requests.get(url, headers=headers)

        response.raise_for_status()

        return response.json()

    build_group_regex = re.compile("fs2_open_.*-builds-([^.-]*)(-([^.]*))?.*")
    source_file_regex = re.compile("fs2_open_.*-source-([^.]*)?.*")

    response = execute_request(
        "/repos/{}/{}/releases/tags/{}".format(config["github"]["user"], config["github"]["repo"], tag_name))

    binary_files = []
    source_files = {}
    for asset in response["assets"]:
        url = asset["browser_download_url"]
        name = asset["name"]

        group_match = build_group_regex.match(name)

        if group_match is not None:
            binary_files.append(ReleaseFile(name, url, group_match.group(1), group_match.group(3)))
        else:
            group_match = source_file_regex.match(name)

            if group_match is None:
                continue

            group = group_match.group(1)

            source_files[group] = SourceFile(name, url, group)

    return binary_files, source_files
