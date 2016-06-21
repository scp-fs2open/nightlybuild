#!/bin/env python3

import argparse
import os
import pickle
import subprocess
import sys
import time

import datetime
import yaml

import bintray
from build_monitor import build_monitor
from nightly_poster import post_nightly

parser = argparse.ArgumentParser()
parser.add_argument("--config", help="Sets the config file", default="config.yml")

args = parser.parse_args()

config = {}

with open(args.config, "r") as f:
    try:
        config = yaml.load(f)
    except yaml.YAMLError as e:
        print(e)
        sys.exit(1)


class ScriptState:
    STATE_INITIAL = "initialization"
    STATE_TAG_PUSHED = "tag_pushed"
    STATE_BUILDS_FINISHED = "builds_finished"
    STATE_POST_CREATED = "post_created"
    STATE_FINISHED = "finished"

    def __init__(self):
        self.tag_name = None

    def load_state(self):
        with open("state.pickle", "rb") as f:
            loaded_state = pickle.load(f)
            self.tag_name = loaded_state[1]
            return loaded_state[0]

    def _exec_git_cmd(self, cmd):
        git_path = config["git"]["repo"]

        return subprocess.check_output(
            "git --git-dir={} --work-tree={} {}".format(os.path.join(git_path, ".git"), git_path, cmd),
            shell=True).strip().decode("ASCII")

    def _get_commit(self):
        git_branch = config["git"]["branch"]

        return self._exec_git_cmd("rev-parse --short {}".format(git_branch)).lower()

    def _get_log(self, pattern):
        tags = self._exec_git_cmd("for-each-ref --sort=-taggerdate --format '%(tag)' refs/tags | grep '{}' | head -n2"
                                  .format(pattern)).splitlines()

        log = self._exec_git_cmd("log {}^..{}^ --no-merges --stat"
                                 " --pretty=format:"
                                 "\"------------------------------------------------------------------------%n"
                                 "commit %h%nAuthor: %an <%ad>%n"
                                 "Commit: %cn <%cd>%n%n    %s\"".format(tags[1], tags[0]))

        return log

    def _go_to_state(self, state):
        """
        Executes the current action and then returns the next state
        :param state: The current state
        :return: The next state that should be used for this function
        """
        if state == ScriptState.STATE_INITIAL:
            date = datetime.datetime.now().strftime("%Y%m%d")

            self.tag_name = "nightly_{}_{}".format(date, self._get_commit())

            git_path = config["git"]["repo"]
            git_branch = config["git"]["branch"]

            # create the tag
            subprocess.call("./tag_nightly.sh '{}' '{}' '{}'".format(git_path, git_branch, self.tag_name), shell=True,
                            stdout=sys.stdout,
                            stderr=sys.stderr)

            return ScriptState.STATE_TAG_PUSHED
        elif state == ScriptState.STATE_TAG_PUSHED:
            # Monitor the created build...
            build_monitor.monitor_builds(self.tag_name, config)

            return ScriptState.STATE_BUILDS_FINISHED
        elif state == ScriptState.STATE_BUILDS_FINISHED:
            # If the build has just finished then Bintray may need some time to actually return all the files
            time.sleep(10.)

            # Get the file list
            files = bintray.get_file_list(self.tag_name, config)

            commit = self._get_commit()
            date = datetime.datetime.now().strftime("%d %B %Y")
            log = self._get_log("nightly_*")

            post_nightly(date, commit, files, log)

            return ScriptState.STATE_POST_CREATED
        elif state == ScriptState.STATE_POST_CREATED:
            return ScriptState.STATE_FINISHED

    def save_state(self, state):
        with open("state.pickle", "wb") as f:
            pickle.dump((state, self.tag_name), f)

    def go_to_state(self, state):
        try:
            current_state = self._go_to_state(state)

            self.save_state(current_state)

            return current_state
        except KeyboardInterrupt:
            self.save_state(state)  # Save the previous state so the next invocation of the script uses the right block
            raise


def state_runner(state, initial_state):
    current_state = initial_state
    while current_state is not ScriptState.STATE_FINISHED:
        current_state = state.go_to_state(current_state)

    os.remove("state.pickle")


with open("state.pickle", "wb") as f:
    pickle.dump((ScriptState.STATE_BUILDS_FINISHED, "nightly_20160621_a633ab9"), f)

script_state = ScriptState()
next_state = None

if os.path.isfile("state.pickle"):
    next_state = script_state.load_state()
else:
    next_state = ScriptState.STATE_INITIAL

state_runner(script_state, next_state)
