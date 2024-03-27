#!/bin/env python3

import argparse
import os
import re
import sys

import semantic_version
import yaml

import file_list
import installer
import nebula
from forum import ForumAPI
from script_state import ScriptState
from util import expand_config_vars

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

parser = argparse.ArgumentParser()
parser.add_argument("--config", help="Sets the config file", default="config.yml")
parser.add_argument("tag_name", help="Overrides the tag name to check. This skips the tag and push phase of the script",
                    default=None, nargs='?')

args = parser.parse_args()

config = {}

MAJOR_VERSION_PATTERN = re.compile("set_if_not_defined\(FSO_VERSION_MAJOR (\d+)\)")
MINOR_VERSION_PATTERN = re.compile("set_if_not_defined\(FSO_VERSION_MINOR (\d+)\)")
BUILD_VERSION_PATTERN = re.compile("set_if_not_defined\(FSO_VERSION_BUILD (\d+)\)")


def _match_version_number(text, regex):
    match = regex.search(text)
    return int(match.group(1))


def get_source_version(config, date_version):
    with open(os.path.join(config["git"]["repo"], "cmake", "version.cmake"), "r") as f:
        filetext = f.read()

        major = _match_version_number(filetext, MAJOR_VERSION_PATTERN)
        minor = _match_version_number(filetext, MINOR_VERSION_PATTERN)
        build = _match_version_number(filetext, BUILD_VERSION_PATTERN)

        return semantic_version.Version("{}.{}.{}-{}".format(major, minor, build, date_version))


with open(args.config, "r") as f:
    try:
        config = yaml.safe_load(f)
        # Support some variables in the config
        expand_config_vars(config)
    except yaml.YAMLError as e:
        print(e)
        sys.exit(1)


class NightlyState(ScriptState):
    def __init__(self):
        super().__init__(config)

    def post_build_actions(self):
        # Get the file list
        files = file_list.get_nightly_files(self.tag_name, config)

        print("Generating installer manifests")
        for file in files:
            installer.get_file_list(file)

        version = get_source_version(self.config, self.date.strftime(ScriptState.DATEFORMAT_VERSION))
        nebula.submit_release(nebula.render_nebula_release(version, "nightly", files, config), config)

        commit = self.repo.get_commit()
        date = self.date.strftime(ScriptState.DATEFORMAT_FORUM)
        log = self.repo.get_log("nightly_*", self.tag_name)

        forum = ForumAPI(self.config)
        forum.post_nightly(date, commit, files, log, self.success)

        return True

    def get_tag_name(self, params):
        return "nightly_{date}_{commit}".format(**params)

    def get_tag_pattern(self):
        return "nightly_*"

    def do_replacements(self, date, current_commit):
        with open(os.path.join(self.config["git"]["repo"], "version_override.cmake"), "w") as test:
            test.write("set(FSO_VERSION_REVISION {})\n".format(date))
            test.write("set(FSO_VERSION_REVISION_STR {}_{})\n".format(date, current_commit))

    def allow_multiple_tags(self):
        return False


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

    # Always use the loaded values to allow changing the config while a script has a serialized state on disk
    script_state.config = config
    script_state.execute()


if __name__ == "__main__":
    main()
