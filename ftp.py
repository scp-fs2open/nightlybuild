import re
from ftplib import FTP, error_perm

from files import ReleaseFile


def get_files(build_type, tag_name, config):
    tag_regex = re.compile("nightly_(.*)")
    build_group_regex = re.compile("nightly_.*-builds-([^.]*).*")

    files = []
    try:
        with FTP(config["ftp"]["host"], config["ftp"]["user"], config["ftp"]["pass"]) as ftp:
            version_str = tag_regex.match(tag_name).group(1)

            path_template = config["ftp"]["path"]
            path = path_template.format(type=build_type, version=version_str)
            file_entries = list(ftp.mlsd(path, ["type"]))

            for entry in file_entries:
                if entry[1]["type"] == "file":
                    files.append(entry[0])
    except error_perm:
        print("Received permanent FTP error!")
        return []

    out_data = []
    for file in files:
        file_match = build_group_regex.match(file)
        if file_match is None:
            print("Ignoring non nightly file '{}'".format(file))
            continue

        group_match = file_match.group(1)
        primary_url = None
        mirrors = []

        for mirror in config["ftp"]["mirrors"]:
            download_url = mirror.format(type=build_type, version=version_str, file=file)
            if primary_url is None:
                primary_url = download_url
            else:
                mirrors.append(download_url)

        out_data.append(ReleaseFile(file, primary_url, group_match, None, mirrors))

    return out_data
