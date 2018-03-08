import os
import pickle

import datetime
import time

import git
from build_monitor import build_monitor


class ScriptState:
    STATE_INITIAL = "initialization"
    STATE_TAG_PUSHED = "tag_pushed"
    STATE_BUILDS_FINISHED = "builds_finished"
    STATE_POST_CREATED = "post_created"
    STATE_FINISHED = "finished"

    DATEFORMAT_VERSION = "%Y%m%d"
    DATEFORMAT_FORUM = "%d %B %Y"

    @staticmethod
    def load_from_file():
        if not os.path.isfile("state.pickle"):
            return None

        with open("state.pickle", "rb") as f:
            return pickle.load(f)

    def __init__(self, config):
        self.config = config
        self.tag_name = None
        self.success = False
        self.state = ScriptState.STATE_INITIAL
        self.repo = git.GitRepository(config["git"]["repo"], config["git"]["branch"])
        self.date = None

    def _go_to_state(self, state):
        """
        Executes the current action and then returns the next state
        :param state: The current state
        :return: The next state that should be used for this function
        """
        if state == ScriptState.STATE_INITIAL:
            self.repo.update_repository()

            latest_commit = self.repo.get_latest_tag_commit(self.get_tag_pattern())
            current_commit = self.repo.get_commit()

            if current_commit == latest_commit:
                print("Latest commit already has a build tag!")
                return ScriptState.STATE_FINISHED

            self.date = datetime.datetime.now()

            format_args = {
                "date": self.date.strftime(ScriptState.DATEFORMAT_VERSION),
                "commit": current_commit
            }

            self.tag_name = self.get_tag_name(format_args)

            restore_state = self.repo.prepare_repo()

            self.do_replacements(self.date.strftime(ScriptState.DATEFORMAT_VERSION), current_commit)

            self.repo.commit_and_tag(self.tag_name)

            self.repo.restore_repo(restore_state)

            return ScriptState.STATE_TAG_PUSHED
        elif state == ScriptState.STATE_TAG_PUSHED:
            # Monitor the created build...
            self.success = build_monitor.monitor_builds(self.tag_name, self.config)

            return ScriptState.STATE_BUILDS_FINISHED
        elif state == ScriptState.STATE_BUILDS_FINISHED:
            if self.post_build_actions():
                return ScriptState.STATE_POST_CREATED
            else:
                return ScriptState.STATE_FINISHED
        elif state == ScriptState.STATE_POST_CREATED:
            return ScriptState.STATE_FINISHED

    def save_state(self, state):
        with open("state.pickle", "wb") as f:
            pickle.dump((state, self.tag_name), f)

    def execute(self):
        while self.state is not ScriptState.STATE_FINISHED:
            previous_state = self.state
            try:
                self.state = self._go_to_state(self.state)

                self.save_to_file()
            except KeyboardInterrupt:
                # Reset state
                self.state = previous_state
                self.save_to_file()  # Save the previous state so the next invocation of the script uses the right block
                raise

        os.remove("state.pickle")

    def save_to_file(self):
        with open("state.pickle", "wb") as f:
            pickle.dump(self, f)

    def post_build_actions(self):
        raise NotImplementedError()

    def get_tag_pattern(self):
        raise NotImplementedError()

    def get_tag_name(self, params):
        raise NotImplementedError()

    def do_replacements(self, date, current_commit):
        raise NotImplementedError()
