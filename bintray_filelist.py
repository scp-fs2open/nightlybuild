#!/bin/env python3
import json
import re

import requests
import argparse

import sys
import yaml

parser = argparse.ArgumentParser()
parser.add_argument("tag_name", help="The tag name to monitor")
parser.add_argument("--config", help="Sets the config file", default="config.yml")

args = parser.parse_args()

config = {}

with open(args.config, "r") as f:
    try:
        config = yaml.load(f)
    except yaml.YAMLError as e:
        print(e)
        sys.exit(1)


def execute_request(path):
    headers = {
    }
    url = "https://bintray.com/api/v1" + path

    response = requests.get(url, headers=headers)

    response.raise_for_status()

    return response.json()

tag_regex = re.compile("nightly_(.*)")
build_group_regex = re.compile("nightly_.*-builds-([^.]*).*")

bintray_version = tag_regex.match(args.tag_name).group(1)

path = "/packages/{subject}/{repo}/{package}/versions/{version}/files".format(**{
    "subject": config["bintray"]["subject"],
    "repo": config["bintray"]["repo"],
    "package": config["bintray"]["package"],
    "version": bintray_version,
})

files = execute_request(path)

out_data = []
for file in files:
    group_match = build_group_regex.match(file["path"]).group(1)
    download_url = "https://dl.bintray.com/{subject}/{repo}/{file_path}".format(**{
        "subject": config["bintray"]["subject"],
        "repo": file["repo"],
        "file_path": file["path"]
    })

    data = {
        "name": file["name"],
        "url": download_url,
        "sha1": file["sha1"],
        "group": group_match
    }
    out_data.append(data)

print(json.dumps(out_data))
