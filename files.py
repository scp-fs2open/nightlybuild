class ReleaseFile:
    def __init__(self, name, url, sha1, group, subgroup=None, tarball=None):
        self.tarball = tarball
        self.subgroup = subgroup
        self.group = group
        self.sha1 = sha1
        self.url = url
        self.name = name
        self.filename = url.split('/')[-1]
