import os.path
import requests

metadata = {
    'type': 'engine',
    'title': 'FSO',
    'notes': '',
    'banner': 'https://fsnebula.org/storage/0d/e7/bf64bcdea9a9c115969cfb784e1ca457d24a7c2da4fc6f213521c3bb6abb.png',
    'screenshots': [],
    'videos': [],
    'first_release': '2017-09-24',
    'cmdline': '',
    'mod_flag': ['FSO'],
    'tile': 'https://fsnebula.org/storage/ec/cc/0bf23e028c26d5175ff52d003bff85b0a17b0ddfc1130d65bdf6d36f6324.png',
    'logo': None,
    'release_thread': None,
    'description': '',
    'id': 'FSO',
    'packages': [],
}

platforms = {
    'Linux': 'linux',
    'MacOSX': 'macosx',
    'Win32': 'windows',
    'Win64': 'windows',
    'Win32-AVX': 'windows',
    'Win64-AVX': 'windows'
}

envs = {
    'Linux': 'linux && x86_64',  # Linux only has 64bit builds
    'MacOSX': 'macosx',
    'Win32': 'windows',
    'Win64': 'windows && x86_64',
    'Win32-AVX': 'windows && avx',
    'Win64-AVX': 'windows && avx && x86_64'
}

subdirs = {
    'Win32': 'x86',
    'Win64': 'x64',
    'Win32-AVX': 'x86_avx',
    'Win64-AVX': 'x64_avx'
}


def render_nebula_release(version, stability, files, config):
    meta = metadata.copy()
    meta['version'] = str(version)
    meta['stability'] = stability  # This can be one of ('stable', 'rc', 'nightly')

    for file in files:
        if file.content_hashes is None:
            # The extraction probably failed which is why we don't have any hashes
            continue

        group = file.group

        # release.py sets subgroup but nightly.py doesn't which means we have to normalize group here.
        if file.subgroup:
            group += '-' + file.subgroup

        pkg = {
            'name': group,
            'notes': '',
            'is_vp': False,
            'files': [{
                'dest': '',
                'filesize': file.size,
                'checksum': ['sha256', file.hash],
                'urls': [file.url] + file.mirrors,
                'filename': file.name
            }],
            'environment': envs.get(group),
            'filelist': [],
            'status': 'required',
            'folder': None,
            'dependencies': [],
            'executables': []
        }

        for fn, checksum in file.content_hashes:
            if group in subdirs:
                dest_fn = subdirs[group] + '/' + fn
            else:
                dest_fn = fn

            # If the group is a known platform then we put the binaries into a separate subfolder for each platform
            if group in platforms:
                dest_fn = platforms[group] + '/' + dest_fn

            pkg['filelist'].append({
                'orig_name': fn,
                'checksum': ('sha256', checksum),
                'archive': file.name,
                'filename': dest_fn
            })

            if group == 'Linux' and fn.endswith('.AppImage'):
                if '-FASTDBG' in fn:
                    label = 'Fast Debug'
                else:
                    label = None

                pkg['executables'].append({
                    'file': dest_fn,
                    'label': label
                })
            elif group == 'MacOSX' and fn.startswith(os.path.basename(fn) + '.app/'):
                if '-FASTDBG' in fn:
                    label = 'Fast Debug'
                else:
                    label = None

                pkg['executables'].append({
                    'file': dest_fn,
                    'label': label
                })
            elif group.startswith('Win') and fn.endswith('.exe'):
                if 'fred2' in fn:
                    if '-FASTDBG' in fn:
                        label = 'FRED2 Debug'
                    else:
                        label = 'FRED2'

                else:
                    if '-FASTDBG' in fn:
                        label = 'Fast Debug'
                    else:
                        label = None

                pkg['executables'].append({
                    'file': dest_fn,
                    'label': label
                })

        meta["packages"].append(pkg)

    return meta


def submit_release(meta, config):
    with requests.session() as session:
        print('Logging into Nebula...')
        result = session.post('https://fsnebula.org/api/1/login', data={
            'user': config['nebula']['user'],
            'password': config['nebula']['password']
        })

        if result.status_code != 200:
            print('Login failed!')
            return False

        data = result.json()
        if not data['result']:
            print('Login failed!')
            return False

        print('Submitting release...')
        result = session.post('https://fsnebula.org/api/1/mod/release', headers={
            'X-KN-TOKEN': data['token']
        }, json=meta)

        if result.status_code != 200:
            print('Request failed!')
            return False

        data = result.json()
        if not data['result']:
            print('ERROR: ' + data['reason'])
            return False

        print('Success!')
        return True
