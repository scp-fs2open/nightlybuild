class ReleaseFile:
    def __init__(self, name, url, group, subgroup=None, tarball=None, mirrors=[]):
        self.mirrors = mirrors
        self.tarball = tarball
        self.subgroup = subgroup
        self.group = group
        self.url = url
        self.name = name
        self.filename = url.split('/')[-1]
