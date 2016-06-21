import requests
import travispy


class Monitor:
    def __init__(self, config, tag_name):
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
        return self.branch.finished

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
    STATUS_RUNNING = "running"
    STATUS_SUCCESS = "success"

    RUNNING_STATES = [STATUS_QUEUED, STATUS_RUNNING]
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

        response = requests.get(url, headers=headers)

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
