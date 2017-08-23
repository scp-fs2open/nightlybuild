class ReleaseFile:
    def __init__(self, name, url, group, subgroup=None, mirrors=None):
        if mirrors is None:
            mirrors = []
        self.mirrors = mirrors
        self.subgroup = subgroup
        self.group = group
        self.url = url
        self.name = name

        self.base_url = "/".join(url.split('/')[0:-1]) + "/"
        self.filename = url.split('/')[-1]


class SourceFile:
    def __init__(self, name, url, group):
        self.group = group
        self.url = url
        self.name = name
