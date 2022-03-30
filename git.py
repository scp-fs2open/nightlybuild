import os
import subprocess

import sys


class GitRepository:
    def __init__(self, path, branch):
        self.branch = branch
        self.path = path

    def _format_git_cmd(self, cmd):
        return "git --git-dir='{}' --work-tree='{}' {}".format(os.path.join(self.path, ".git"), self.path, cmd)

    def _git_get_output(self, cmd):
        return subprocess.check_output(self._format_git_cmd(cmd), shell=True).strip().decode("UTF-8")

    def _git_redirected(self, cmd):
        print(">> git " + cmd)
        return subprocess.call(self._format_git_cmd(cmd), shell=True, stdout=sys.stdout, stderr=sys.stderr,
                               stdin=sys.stdin)

    def _git_redirected_success(self, cmd):
        ret = self._git_redirected(cmd)

        assert ret == 0

    def get_commit(self):
        return self._git_get_output("rev-parse --short {}".format(self.branch)).lower()

    def get_log(self, pattern, tag_name):
        tags = self._git_get_output("for-each-ref --sort=-taggerdate --format '%(tag)' refs/tags | grep '{}' | grep -A 1 {}"
                                    .format(pattern, tag_name)).splitlines()
        
        if len(tags) < 2:
            return "No log available"
        
        return self._git_get_output("log {}^..{}^ --no-merges --stat"
                                    " --pretty=format:"
                                    "\"------------------------------------------------------------------------%n"
                                    "commit %h%nAuthor: %an <%ad>%n"
                                    "Commit: %cn <%cd>%n%n    %s\"".format(tags[1], tags[0]))

    def get_latest_tag_name(self, pattern) -> str:
        """
        @brief Retrieves the name of the most recent version tag commit.
        """
        return self._git_get_output("for-each-ref --sort=-taggerdate --format '%(tag)' refs/tags | grep '{}' | head -n1"
                                   .format(pattern))

    def get_latest_tag_commit(self, pattern):
        """
        @brief Retrieves the SHA of the most recent version tag commit.
        """
        tag = self.get_latest_tag_name(pattern)

        if len(tag) < 1:
            return ""

        return self._git_get_output("rev-parse --short {}^".format(tag))

    def update_repository(self):
        """
        @brief Updates the local repo to the most recent commit and deletes any untracked changes
        """
        self._git_redirected_success("checkout '{}'".format(self.branch))
        self._git_redirected_success("fetch --tags origin".format(self.branch))
        self._git_redirected_success("reset --hard 'origin/{}'".format(self.branch))

    def prepare_repo(self):
        self._git_redirected_success("checkout '{}'".format(self.branch))

        has_changes = self._git_redirected("diff-index --quiet HEAD --") != 0

        stashed_changes = False
        if has_changes:
            print("Stashing local changes for later recovery")
            self._git_redirected_success("stash -u -a")
            stashed_changes = True

        # Detach HEAD so we don't change the branch we are on
        self._git_redirected_success("checkout --detach")

        return stashed_changes

    def commit_and_tag(self, tag_name):
        """
        @brief  Commit, tag (annotated), and push to origin/repo
        """
        
        self._git_redirected_success("add .")
        self._git_redirected_success(
            "commit -m 'Automated build commit' --author='SirKnightly <SirKnightlySCP@gmail.com>'")
        self._git_redirected_success("tag -a '{}' -m 'Build script tag'".format(tag_name))
        self._git_redirected_success("push --tags")

    def restore_repo(self, stashed_changes):
        self._git_redirected_success("checkout '{}'".format(self.branch))

        if stashed_changes:
            print("Restoring previous changes")
            self._git_redirected_success("stash pop")
