import ftplib

import re

from files import ReleaseFile


def get_files(build_type, tag_name, config):
    tag_regex = re.compile("nightly_(.*)")
    build_group_regex = re.compile("nightly_.*-builds-([^.]*).*")

    ftp = ftplib.FTP(config["ftp"]["host"])
    ftp.login(config["ftp"]["user"], config["ftp"]["pass"])

    version_str = tag_regex.match(tag_name).group(1)

    path_template = config["ftp"]["path"]
    path = path_template.format(type=build_type, version=version_str)
    file_entries = list(ftp.mlsd(path))

    files = []
    for entry in file_entries:
        if entry[1]["type"] == "file":
            files.append(entry[0])

    ftp.quit()

    out_data = []
    for file in files:
        group_match = build_group_regex.match(file).group(1)
        primary_url = None
        mirrors = []

        for mirror in config["ftp"]["mirrors"]:
            download_url = mirror.format(type=build_type, version=version_str, file=file)
            if primary_url is None:
                primary_url = download_url
            else:
                mirrors.append(download_url)

        out_data.append(ReleaseFile(file, primary_url, group_match, None, None, mirrors))

    return out_data
