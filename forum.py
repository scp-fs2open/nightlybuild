from mako.template import Template


def read_text(file):
    with open(file, "r") as f:
        return f.read()

class ForumAPI:
    def __init__(self, config):
        self.config = config

    def login(self):
        raise NotImplementedError()

    def post_nightly(self, date, revision, files, log):
        template = Template(read_text("templates/nightly.txt"))

        rendered = template.render(**{
            "date": date,
            "revision": revision,
            "files": files,
            "log": log
        })

        print(rendered)

    def post_release(self):
        raise NotImplementedError()

"""
import mechanicalsoup


browser = mechanicalsoup.Browser()

login_page = browser.get("http://www.hard-light.net/forums/index.php?action=login")

login_form = mechanicalsoup.Form(login_page.soup.select("#frmLogin")[0])
login_form.input({"user": "m!m", "passwrd": "8FHkjaERP4E9WWayDz5B", "cookielength": 60})

page2 = browser.submit(login_form)

print(page2.url)
"""
