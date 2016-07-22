#!/bin/env python3

import argparse
import os
import sys
import time

import datetime
import yaml
import semantic_version

import bintray
import github
from script_state import ScriptState




parser = argparse.ArgumentParser()
parser.add_argument("--config", help="Sets the config file", default="config.yml")
parser.add_argument("version", help="The version to mark this release as")
parser.add_argument("tag_name", help="Overrides the tag name to check. This skips the tag and push phase of the script",
                    default=None, nargs='?')

args = parser.parse_args()

config = {}

with open(args.config, "r") as f:
    try:
        config = yaml.load(f)
    except yaml.YAMLError as e:
        print(e)
        sys.exit(1)


class ReleaseState(ScriptState):
    def __init__(self, version):
        super().__init__(config)
        self.version = version

    def post_build_actions(self):
        # Get the file list
        files = github.get_release_files(self.tag_name, config)

        print(files)

        commit = self.repo.get_commit()
        date = datetime.datetime.now().strftime("%d %B %Y")
        log = self.repo.get_log("nightly_*")

        #post_nightly(date, commit, files, log)

    def get_tag_name(self, params):
        base = "release_{}_{}_{}".format(self.version.major, self.version.minor, self.version.patch)

        if len(self.version.prerelease) > 0:
            base += "_" + "_".join(self.version.prerelease)

        return base

    def get_tag_pattern(self):
        return "release_*"

    def do_replacements(self, date, current_commit):
        with open(os.path.join(self.config["git"]["repo"], "version_override.cmake"), "a") as test:
            test.write("set(FSO_VERSION_MAJOR {})\n".format(self.version.major))
            test.write("set(FSO_VERSION_MINOR {})\n".format(self.version.minor))
            test.write("set(FSO_VERSION_BUILD {})\n".format(self.version.patch))
            test.write("set(FSO_VERSION_REVISION 0)\n")
            test.write("set(FSO_VERSION_REVISION_STR {})\n".format("-".join(self.version.prerelease)))


def main():
    script_state = ScriptState.load_from_file()

    if not semantic_version.validate(args.version):
        print("Specified version is not a valid version string!")
        return

    version = semantic_version.Version(args.version)
    if script_state is None:
        # An existing script state overrides the commandline argument
        if args.tag_name is not None:
            script_state = ReleaseState(version)
            script_state.state = ScriptState.STATE_TAG_PUSHED
            script_state.tag_name = args.tag_name
        else:
            if script_state is None:
                script_state = ReleaseState(version)
    else:
        if args.tag_name:
            print("Tag name ignored because there was a stored script state.")

        if not isinstance(script_state, ReleaseState):
            print("State object is not a nightly state! Delete 'state.pickle' or execute right script.")
            return

    script_state.execute()


if __name__ == "__main__":
    main()
