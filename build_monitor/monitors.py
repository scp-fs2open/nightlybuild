import github
import requests
from github import Github

from util import GLOBAL_TIMEOUT


class Monitor:
    tag_name: str

    def __init__(self, config, tag_name: str):
        self.config = config
        self.tag_name = tag_name

    def update_state(self):
        raise NotImplementedError()

    @property
    def running(self):
        raise NotImplementedError()

    @property
    def success(self):
        raise NotImplementedError()

    @property
    def errored(self):
        raise NotImplementedError()

    @property
    def state(self):
        raise NotImplementedError()

    @property
    def name(self):
        raise NotImplementedError()


class GitHubMonitor(Monitor):
    def __init__(self, config, tag_name):
        super().__init__(config, tag_name)

        self.github = Github(config["github"]["token"])
        self.repo = self.github.get_repo(self.config["github"]["user"] + "/" + self.config["github"]["repo"])

        self.status = None
        self.result = None

    def update_state(self):
        # Check tag name and set filename
        filename = ""
        if self.tag_name.startswith("nightly_"):
            filename = "build-nightly.yaml"
        elif self.tag_name.startswith("release_"):
            filename = "build-release.yaml"
        else:
            raise Exception("Invalid tag name {}: Expected a \'release_\' or \'nightly_\' prefix.".format(self.tag_name))

        # Find the workflow by filename
        dist_workflow = None
        for workflow in self.repo.get_workflows():
            if workflow.path == (".github/workflows/" + filename):
                dist_workflow = workflow
                break

        if dist_workflow is None:
            raise Exception("Could not find {} within workflow index".format(filename))

        # Get the run history made by this workflow
        runs = dist_workflow.get_runs()

        if runs.totalCount == 0:
            raise Exception("{} has been not run yet".format(filename))

        # Find the most recent run for the given tag_name
        # Assumes runs are ordered from most recent to oldest
        current_run = None
        for r in runs:
            if r.head_branch == self.tag_name:
                current_run = r
                break
        
        if current_run == None:
            raise Exception("{} has not been run yet for tag {}".format(filename, self.tag_name))

        # Set the status and result members accordign to the most recent run result
        self.status = current_run.status
        self.result = current_run.conclusion

    @property
    def running(self):
        if self.status is None:
            # Start may still be pending
            return True

        return self.status != "completed"

    @property
    def success(self):
        if self.result is None:
            return False

        return self.result == "success"

    @property
    def errored(self):
        if self.result is None:
            return False

        return self.result != "success"

    @property
    def state(self):
        if self.status is None:
            return "Unknown"

        if self.running:
            return self.status
        else:
            return self.result

    @property
    def name(self):
        return "GitHub Actions ({})".format(self.repo.full_name)
