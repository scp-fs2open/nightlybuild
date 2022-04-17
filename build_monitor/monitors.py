import github
import requests
import travispy
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


class TravisMonitor(Monitor):
    def __init__(self, config, tag_name):
        super().__init__(config, tag_name)
        self.travis = travispy.TravisPy()
        self.branch = None

    def update_state(self):
        self.branch = self.travis.branch(self.tag_name, self.config["travis"]["slug"])

    @property
    def running(self):
        return (self.branch.pending or self.branch.queued or self.branch.started or self.branch.running) and not (
                self.success or self.errored)

    @property
    def success(self):
        return self.branch.passed

    @property
    def errored(self):
        return self.branch.errored or self.branch.failed

    @property
    def state(self):
        return self.branch.state

    @property
    def name(self):
        return "Travis CI"


class AppveyorMonitor(Monitor):
    STATUS_QUEUED = "queued"
    STATUS_STARTING = "starting"
    STATUS_RUNNING = "running"
    STATUS_SUCCESS = "success"

    RUNNING_STATES = [STATUS_QUEUED, STATUS_STARTING, STATUS_RUNNING]
    SUCCESS_STATES = [STATUS_SUCCESS]

    def __init__(self, config, tag_name):
        super().__init__(config, tag_name)
        self.status = None

    def execute_request(self, path):
        headers = {
            "Authorization": "Bearer " + self.config["appveyor"]["token"],
            "Content-type": "application/json"
        }
        url = "https://ci.appveyor.com/api" + path

        response = requests.get(url, headers=headers, timeout=GLOBAL_TIMEOUT)

        response.raise_for_status()

        return response.json()

    def update_state(self):
        response = self.execute_request(
            "/projects/{}/{}/branch/{}".format(self.config["appveyor"]["user"], self.config["appveyor"]["repo"],
                                               self.tag_name))

        self.status = response["build"]["status"]

    @property
    def running(self):
        return self.status in AppveyorMonitor.RUNNING_STATES

    @property
    def errored(self):
        return self.status not in AppveyorMonitor.RUNNING_STATES and self.status not in AppveyorMonitor.SUCCESS_STATES

    @property
    def success(self):
        return self.status in AppveyorMonitor.SUCCESS_STATES

    @property
    def state(self):
        return self.status

    @property
    def name(self):
        return "Appveyor"


class GitHubMonitor(Monitor):
    def __init__(self, config, tag_name):
        super().__init__(config, tag_name)

        self.github = Github(config["github"]["token"])
        self.repo = self.github.get_repo(self.config["github"]["user"] + "/" + self.config["github"]["repo"])

        self.status = None
        self.result = None

    def update_state(self):
        dist_workflow = None
        filename = ""

        if self.tag_name.startswith("nightly_"):
            filename = "build-nightly.yaml"
        elif self.tag_name.startswith("release_"):
            filename = "build-release.yaml"
        else:
            raise Exception("Invalid tag name. Not a \'release_\' or \'nightly_\'")

        for workflow in self.repo.get_workflows():
            if self.tag_name.startswith("nightly_") and workflow.path == ".github/workflows/build-nightly.yaml":
                dist_workflow = workflow
                break
            if self.tag_name.startswith("release_") and workflow.path == ".github/workflows/build-release.yaml":
                dist_workflow = workflow
                break

        if dist_workflow is None:
            raise Exception("Could not find {} within workflow index".format(filename))

        runs = dist_workflow.get_runs(branch=self.tag_name)

        if runs.totalCount == 0:
            raise Exception("{} has been not run yet for {}".format(filename, self.tag_name))

        current_run = runs[0]

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
