import re
import time
from itertools import groupby

from mako.template import Template
from mako import exceptions
import requests


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

    def login(self, session):
        data = {
            "user": self.config["hlp"]["user"],
            "passwrd": self.config["hlp"]["pass"]
        }
        session.post("http://www.hard-light.net/forums/index.php?action=login2", data=data)

        time.sleep(10.)

    def create_post(self, session, title, content, board):
        response = session.get(self.config["hlp"]["board_url_format"].format(board=board))

        # This part of the code was taken from https://github.com/Chaturaphut/Python-SMF-Auto-Post/blob/master/smf_post.py
        seq = re.search('name="seqnum" value="(.+?)"', response.text).group(1)
        sesVar = re.search('sSessionVar: \'(.+?)\'', response.text).group(1)
        sesID = re.search('sSessionId: \'(.+?)\'', response.text).group(1)

        field = {'topic': '0', 'subject': title, 'icon': 'xx', 'sel_face': '', 'sel_size': '', 'sell_color': '',
                 'message': content, 'message_mode': '0', 'notify': '0', 'lock': '0', 'sticky': '0', 'move': '0',
                 'additional_options': '0', sesVar: sesID, 'seqnum': seq}

        print("Posting to " + self.config["hlp"]["post_action"].format(board=board))
        return session.post(self.config["hlp"]["post_action"].format(board=board), data=field)

    def post_nightly(self, date, revision, files, log, success):
        print("Posting nightly thread...")

        with requests.session() as session:
            print("Logging in...")
            self.login(session)

            time.sleep(10.)

            title = "Nightly: {} - Revision {}".format(date, revision)

            template = Template(filename=self.config["templates"]["nightly"])
            rendered = template.render(**{
                "date": date,
                "revision": revision,
                "files": files,
                "log": log,
                "success": success
            })

            print("Creating post...")
            self.create_post(session, title, rendered, self.config["nightly"]["hlp_board"])

    def post_release(self, date, version, files):
        print("Posting release thread...")

        # Construct the file groups
        groups = dict(((x[0], FileGroup(x[0], list(x[1]))) for x in groupby(files, lambda g: g.group)))

        with requests.session() as session:
            print("Logging in...")
            self.login(session)

            time.sleep(10.)

            title = "Release: {}".format(version)

            template = Template(filename=self.config["templates"]["release"], module_directory='/tmp/mako_modules')
            rendered = template.render(**{
                "date": date,
                "version": version,
                "files": files,
                "groups": groups,
            }).strip("\n")

            print("Creating post...")

            self.create_post(session, title, rendered, self.config["release"]["hlp_board"])
