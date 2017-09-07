import hashlib
import tarfile
import zipfile
from tempfile import NamedTemporaryFile
from zipfile import ZipFile

import requests
from mako.template import Template

from files import ReleaseFile


def _download_file(url, dest_file):
    print("Downloading " + url)
    # NOTE the stream=True parameter
    r = requests.get(url, stream=True)
    for chunk in r.iter_content(chunk_size=1024):
        if chunk:  # filter out keep-alive new chunks
            dest_file.write(chunk)
    dest_file.flush()


def get_file_list(file: ReleaseFile, hash_alg: str = "sha256"):
    with NamedTemporaryFile('wb', suffix=file.filename) as local_file:
        _download_file(file.url, local_file)

        filename = local_file.name
        hash_list = []

        if tarfile.is_tarfile(filename):
            with tarfile.open(filename) as archive:
                for entry in archive:
                    if not entry.isfile():
                        continue

                    fileobj = archive.extractfile(entry)

                    h = hashlib.new(hash_alg)
                    while True:
                        data = fileobj.read(4096)

                        if not data:
                            break

                        h.update(data)

                    hash_list.append((entry.path, h.hexdigest()))

                return hash_list
        elif zipfile.is_zipfile(filename):
            with ZipFile(filename) as archive:
                for entry in archive.infolist():
                    # Python 3.6 has is_dir but that version is relatively new so we'll use the "safe" version here
                    if entry.filename.endswith('/'):
                        continue

                    h = hashlib.new(hash_alg)
                    with archive.open(entry) as fileobj:
                        while True:
                            data = fileobj.read(4096)

                            if not data:
                                break

                            h.update(data)

                    hash_list.append((entry.filename, h.hexdigest()))

                return hash_list
        else:
            raise NotImplementedError("Unsupported archive type!")


def render_installer_config(version, groups, config):
    template = Template(filename=config["templates"]["installer"], module_directory='/tmp/mako_modules')
    return template.render(**{
        "version": version,
        "groups": groups,
    }).strip("\n")
