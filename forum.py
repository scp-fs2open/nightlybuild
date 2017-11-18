
import time
from itertools import groupby

from mako.template import Template
from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver


class FileGroup:
    def __init__(self, name, files):
        self.files = files
        self.name = name

        if len(files) == 1:
            self.mainFile = files[0]
            self.subFiles = {}
        else:
            self.mainFile = None
            subFiles = []
            for file in files:
                if file.subgroup is None:
                    self.mainFile = file
                else:
                    subFiles.append(file)

            self.subFiles = dict(((x[0], next(x[1])) for x in groupby(subFiles, lambda f: f.subgroup)))


def read_text(file):
    with open(file, "r") as f:
        return f.read()


def get_form_with_fields(browser, *kwargs):
    forms = browser.get_forms()

    for form in forms:
        keys = list(form.keys())

        if all((field in keys for field in kwargs)):
            return form

    return None


class ForumAPI:
    def __init__(self, config):
        self.config = config

    def _create_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')

        return webdriver.PhantomJS(executable_path=self.config["phantomjs"]["path"])

    def login(self, driver: WebDriver):
        driver.get("http://www.hard-light.net/forums/index.php?action=login")

        driver.save_screenshot("/tmp/pre_login.png")

        form = driver.find_element_by_id("frmLogin")

        form.find_element_by_name("user").send_keys(self.config["hlp"]["user"])
        form.find_element_by_name("passwrd").send_keys(self.config["hlp"]["pass"])

        form.submit()

        driver.save_screenshot("/tmp/post_login.png")

        time.sleep(3.)

    def create_post(self, driver: WebDriver, title, content, board):
        driver.get(self.config["hlp"]["board_url_format"].format(board=board))

        form = driver.find_element_by_id("postmodify")
        form.find_element_by_name("subject").send_keys(title)
        form.find_element_by_name("message").send_keys(content)

        driver.save_screenshot("/tmp/pre_post.png")

        form.submit()

        driver.save_screenshot("/tmp/post_post.png")

    def post_nightly(self, date, revision, files, log, success):
        print("Posting nightly thread...")

        driver = self._create_driver()
        print("Logging in...")

        self.login(driver)

        title = "Nightly: {} - Revision {}".format(date, revision)

        template = Template(filename=self.config["templates"]["nightly"])
        rendered = template.render(**{
            "date": date,
            "revision": revision,
            "files": files,
            "log": log,
            "success": success
        })

        print(rendered)

        print("Creating post...")
        self.create_post(driver, title, rendered, self.config["nightly"]["hlp_board"])

        driver.close()

    def post_release(self, date, version, groups, sources):
        print("Posting release thread...")

        driver = self._create_driver()
        print("Logging in...")

        self.login(driver)

        title = "Release: {}".format(version)

        template = Template(filename=self.config["templates"]["release"], module_directory='/tmp/mako_modules')
        rendered = template.render(**{
            "date": date,
            "version": version,
            "groups": groups,
            "sources": sources
        }).strip("\n")

        print("Creating post...")

        self.create_post(driver, title, rendered, self.config["release"]["hlp_board"])
