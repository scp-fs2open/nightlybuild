#!/bin/env python3

import argparse
import os
import sys
import time

import datetime
import yaml

import bintray
from nightly_poster import post_nightly
from script_state import ScriptState

parser = argparse.ArgumentParser()
parser.add_argument("--config", help="Sets the config file", default="config.yml")
parser.add_argument("tag_name", help="Overrides the tag name to check. This skips the tag and push phase of the script",
                    default=None)

args = parser.parse_args()

config = {}

with open(args.config, "r") as f:
    try:
        config = yaml.load(f)
    except yaml.YAMLError as e:
        print(e)
        sys.exit(1)


class NightlyState(ScriptState):
    def __init__(self):
        super().__init__(config)

    def post_build_actions(self):
        # Get the file list
        files = bintray.get_file_list(self.tag_name, config)

        commit = self.repo.get_commit()
        date = datetime.datetime.now().strftime("%d %B %Y")
        log = self.repo.get_log("nightly_*")

        post_nightly(date, commit, files, log)

    def get_tag_format(self):
        return "nightly_{date}_{commit}"

    def get_tag_pattern(self):
        return "nightly_*"

    def do_replacements(self):
        with open(os.path.join(self.config["git"]["repo"], "configure.ac"), "a") as test:
            test.write("dnl Test change\n")


def main():
    script_state = ScriptState.load_from_file()
    if script_state is None:
        # An existing script state overrides the commandline argument
        if args.tag_name is not None:
            script_state = NightlyState()
            script_state.state = ScriptState.STATE_TAG_PUSHED
            script_state.tag_name = args.tag_name
        else:
            if script_state is None:
                script_state = NightlyState()
    else:
        if args.tag_name:
            print("Tag name ignored because there was a stored script state.")

        if not isinstance(script_state, NightlyState):
            print("State object is not a nightly state! Delete 'state.pickle' or execute right script.")
            return

    script_state.execute()


if __name__ == "__main__":
    main()
