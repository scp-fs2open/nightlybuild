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

        # A list of tuples of (filename, hash)
        self.content_hashes = None


class SourceFile:
    def __init__(self, name, url, group):
        self.group = group
        self.url = url
        self.name = name
