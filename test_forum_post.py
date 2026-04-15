#!/usr/bin/env python3
"""
Reconstruct and optionally send a realistic nightly forum post payload.
Uses the same code paths as nightly.py to generate the exact same content.

Usage:
  python test_forum_post.py                    # just print the payload
  python test_forum_post.py --post             # actually post it to the forum
  python test_forum_post.py --tag nightly_20260413_abb9dfb78  # use a specific tag
"""

import argparse
import os
import sys

# Run from script directory so imports work
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

import yaml
import requests
from mako.template import Template

import file_list
from git import GitRepository

parser = argparse.ArgumentParser(description="Test nightly forum post payload")
parser.add_argument("--tag", default="nightly_20260413_abb9dfb78",
                    help="Nightly tag to use for file list (default: nightly_20260413_abb9dfb78)")
parser.add_argument("--post", action="store_true",
                    help="Actually POST to the forum (default: just print payload)")
parser.add_argument("--api-url", default="http://example.tld/path/to/post_api.php",
                    help="Forum API URL")
parser.add_argument("--api-key", default=None,
                    help="Forum API key (required if --post)")
parser.add_argument("--board", default="173", help="Board ID (default: 173)")
parser.add_argument("--fs2-repo", default="~/code/fs2_open",
                    help="Path to fs2open.github.com repo (for git log)")
parser.add_argument("--branch", default="master", help="Branch name (default: master)")
args = parser.parse_args()
args.fs2_repo = os.path.expanduser(args.fs2_repo)

# Load mirrors and template path from sample config so they stay in sync
with open("config.yml.sample", "r") as f:
    config = yaml.safe_load(f)

# --- Fetch the real file list ---
print("=== Fetching file list for tag: {} ===".format(args.tag))
files = file_list.get_nightly_files(args.tag, config)

if not files:
    print("ERROR: No files found for tag {}".format(args.tag))
    sys.exit(1)

print("Found {} files:".format(len(files)))
for f in files:
    print("  {} ({})".format(f.name, f.group))

# --- Get the real git log ---
print("\n=== Generating git log from {} ===".format(args.fs2_repo))
repo = GitRepository(args.fs2_repo, args.branch)
log = repo.get_log("nightly_*", args.tag)

# --- Derive date and revision from the tag ---
import re
import datetime
tag_match = re.match(r"nightly_(\d{4})(\d{2})(\d{2})_(.+)", args.tag)
if not tag_match:
    print("ERROR: Tag '{}' doesn't match expected nightly_YYYYMMDD_commit format".format(args.tag))
    sys.exit(1)
date = datetime.date(int(tag_match.group(1)), int(tag_match.group(2)), int(tag_match.group(3))).strftime("%d %B %Y")
revision = tag_match.group(4)
success = True

template = Template(filename=config["templates"]["nightly"])
rendered = template.render_unicode(**{
    "date": date,
    "revision": revision,
    "files": files,
    "log": log,
    "success": success,
})

# --- Build the subject ---
title = "Nightly: {} - Revision {}".format(date, revision)

# --- Display the payload ---
print("\n=== SUBJECT ===")
print(title)
print("\n=== BODY ({} chars) ===".format(len(rendered)))
print(rendered)
print("\n=== END BODY ===")

# --- Build the POST data dict (exactly as forum.py does) ---
post_data = {
    "api_key": args.api_key or "<API_KEY_PLACEHOLDER>",
    "board": args.board,
    "subject": title,
    "body": rendered,
}

print("\n=== POST data field sizes ===")
for k, v in post_data.items():
    print("  {}: {} chars".format(k, len(str(v))))

if args.post:
    if not args.api_key:
        print("\nERROR: --api-key is required when using --post")
        sys.exit(1)

    print("\n=== Sending POST to {} ===".format(args.api_url))
    try:
        resp = requests.post(args.api_url, data=post_data)
        print("HTTP Status: {}".format(resp.status_code))
        print("Response headers: {}".format(dict(resp.headers)))
        print("Response body: '{}'".format(resp.text))
        print("\nresp.text == 'OK'? {}".format(resp.text == "OK"))
    except Exception as e:
        print("Request failed with exception: {}".format(e))
else:
    print("\nDry run — use --post --api-key=YOUR_KEY to actually send")
