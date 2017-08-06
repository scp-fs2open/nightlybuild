import unittest

import requests_mock
import github

# This data will be returned by our requests mock
# It's based on real data returned by the GitHub API but where the name and repository have been changed to fit the test
TEST_API_DATA = """
{
  "url": "https://api.github.com/repos/test/test/releases/7002287",
  "assets_url": "https://api.github.com/repos/test/test/releases/7002287/assets",
  "upload_url": "https://uploads.github.com/repos/test/test/releases/7002287/assets{?name,label}",
  "html_url": "https://github.com/test/test/releases/tag/release_test",
  "id": 7002287,
  "tag_name": "release_test",
  "target_commitish": "master",
  "name": null,
  "draft": false,
  "author": {
    "login": "SirKnightly",
    "id": 20561911,
    "avatar_url": "https://avatars1.githubusercontent.com/u/20561911?v=4",
    "gravatar_id": "",
    "url": "https://api.github.com/users/SirKnightly",
    "html_url": "https://github.com/SirKnightly",
    "followers_url": "https://api.github.com/users/SirKnightly/followers",
    "following_url": "https://api.github.com/users/SirKnightly/following{/other_user}",
    "gists_url": "https://api.github.com/users/SirKnightly/gists{/gist_id}",
    "starred_url": "https://api.github.com/users/SirKnightly/starred{/owner}{/repo}",
    "subscriptions_url": "https://api.github.com/users/SirKnightly/subscriptions",
    "organizations_url": "https://api.github.com/users/SirKnightly/orgs",
    "repos_url": "https://api.github.com/users/SirKnightly/repos",
    "events_url": "https://api.github.com/users/SirKnightly/events{/privacy}",
    "received_events_url": "https://api.github.com/users/SirKnightly/received_events",
    "type": "User",
    "site_admin": false
  },
  "prerelease": false,
  "created_at": "2017-07-11T16:45:30Z",
  "published_at": "2017-07-11T16:57:36Z",
  "assets": [
    {
      "url": "https://api.github.com/repos/test/test/releases/assets/4303960",
      "id": 4303960,
      "name": "fs2_open_test-builds-Linux.tar.gz",
      "label": "",
      "uploader": {
        "login": "SirKnightly",
        "id": 20561911,
        "avatar_url": "https://avatars1.githubusercontent.com/u/20561911?v=4",
        "gravatar_id": "",
        "url": "https://api.github.com/users/SirKnightly",
        "html_url": "https://github.com/SirKnightly",
        "followers_url": "https://api.github.com/users/SirKnightly/followers",
        "following_url": "https://api.github.com/users/SirKnightly/following{/other_user}",
        "gists_url": "https://api.github.com/users/SirKnightly/gists{/gist_id}",
        "starred_url": "https://api.github.com/users/SirKnightly/starred{/owner}{/repo}",
        "subscriptions_url": "https://api.github.com/users/SirKnightly/subscriptions",
        "organizations_url": "https://api.github.com/users/SirKnightly/orgs",
        "repos_url": "https://api.github.com/users/SirKnightly/repos",
        "events_url": "https://api.github.com/users/SirKnightly/events{/privacy}",
        "received_events_url": "https://api.github.com/users/SirKnightly/received_events",
        "type": "User",
        "site_admin": false
      },
      "content_type": "application/gzip",
      "state": "uploaded",
      "size": 19754718,
      "download_count": 26,
      "created_at": "2017-07-11T16:57:34Z",
      "updated_at": "2017-07-11T16:57:36Z",
      "browser_download_url": "https://github.com/test/test/releases/download/release_test/fs2_open_test-builds-Linux.tar.gz"
    },
    {
      "url": "https://api.github.com/repos/test/test/releases/assets/4304135",
      "id": 4304135,
      "name": "fs2_open_test-builds-MacOSX.tar.gz",
      "label": "",
      "uploader": {
        "login": "SirKnightly",
        "id": 20561911,
        "avatar_url": "https://avatars1.githubusercontent.com/u/20561911?v=4",
        "gravatar_id": "",
        "url": "https://api.github.com/users/SirKnightly",
        "html_url": "https://github.com/SirKnightly",
        "followers_url": "https://api.github.com/users/SirKnightly/followers",
        "following_url": "https://api.github.com/users/SirKnightly/following{/other_user}",
        "gists_url": "https://api.github.com/users/SirKnightly/gists{/gist_id}",
        "starred_url": "https://api.github.com/users/SirKnightly/starred{/owner}{/repo}",
        "subscriptions_url": "https://api.github.com/users/SirKnightly/subscriptions",
        "organizations_url": "https://api.github.com/users/SirKnightly/orgs",
        "repos_url": "https://api.github.com/users/SirKnightly/repos",
        "events_url": "https://api.github.com/users/SirKnightly/events{/privacy}",
        "received_events_url": "https://api.github.com/users/SirKnightly/received_events",
        "type": "User",
        "site_admin": false
      },
      "content_type": "application/gzip",
      "state": "uploaded",
      "size": 20312518,
      "download_count": 5,
      "created_at": "2017-07-11T17:24:46Z",
      "updated_at": "2017-07-11T17:24:49Z",
      "browser_download_url": "https://github.com/test/test/releases/download/release_test/fs2_open_test-builds-MacOSX.tar.gz"
    },
    {
      "url": "https://api.github.com/repos/test/test/releases/assets/4304097",
      "id": 4304097,
      "name": "fs2_open_test-builds-Win32-AVX.zip",
      "label": "",
      "uploader": {
        "login": "SirKnightly",
        "id": 20561911,
        "avatar_url": "https://avatars1.githubusercontent.com/u/20561911?v=4",
        "gravatar_id": "",
        "url": "https://api.github.com/users/SirKnightly",
        "html_url": "https://github.com/SirKnightly",
        "followers_url": "https://api.github.com/users/SirKnightly/followers",
        "following_url": "https://api.github.com/users/SirKnightly/following{/other_user}",
        "gists_url": "https://api.github.com/users/SirKnightly/gists{/gist_id}",
        "starred_url": "https://api.github.com/users/SirKnightly/starred{/owner}{/repo}",
        "subscriptions_url": "https://api.github.com/users/SirKnightly/subscriptions",
        "organizations_url": "https://api.github.com/users/SirKnightly/orgs",
        "repos_url": "https://api.github.com/users/SirKnightly/repos",
        "events_url": "https://api.github.com/users/SirKnightly/events{/privacy}",
        "received_events_url": "https://api.github.com/users/SirKnightly/received_events",
        "type": "User",
        "site_admin": false
      },
      "content_type": "application/octet-stream",
      "state": "uploaded",
      "size": 18995998,
      "download_count": 31,
      "created_at": "2017-07-11T17:17:06Z",
      "updated_at": "2017-07-11T17:17:08Z",
      "browser_download_url": "https://github.com/test/test/releases/download/release_test/fs2_open_test-builds-Win32-AVX.zip"
    },
    {
      "url": "https://api.github.com/repos/test/test/releases/assets/4303987",
      "id": 4303987,
      "name": "fs2_open_test-builds-Win32.zip",
      "label": "",
      "uploader": {
        "login": "SirKnightly",
        "id": 20561911,
        "avatar_url": "https://avatars1.githubusercontent.com/u/20561911?v=4",
        "gravatar_id": "",
        "url": "https://api.github.com/users/SirKnightly",
        "html_url": "https://github.com/SirKnightly",
        "followers_url": "https://api.github.com/users/SirKnightly/followers",
        "following_url": "https://api.github.com/users/SirKnightly/following{/other_user}",
        "gists_url": "https://api.github.com/users/SirKnightly/gists{/gist_id}",
        "starred_url": "https://api.github.com/users/SirKnightly/starred{/owner}{/repo}",
        "subscriptions_url": "https://api.github.com/users/SirKnightly/subscriptions",
        "organizations_url": "https://api.github.com/users/SirKnightly/orgs",
        "repos_url": "https://api.github.com/users/SirKnightly/repos",
        "events_url": "https://api.github.com/users/SirKnightly/events{/privacy}",
        "received_events_url": "https://api.github.com/users/SirKnightly/received_events",
        "type": "User",
        "site_admin": false
      },
      "content_type": "application/octet-stream",
      "state": "uploaded",
      "size": 19006624,
      "download_count": 152,
      "created_at": "2017-07-11T17:01:24Z",
      "updated_at": "2017-07-11T17:01:26Z",
      "browser_download_url": "https://github.com/test/test/releases/download/release_test/fs2_open_test-builds-Win32.zip"
    },
    {
      "url": "https://api.github.com/repos/test/test/releases/assets/4304325",
      "id": 4304325,
      "name": "fs2_open_test-builds-Win64-AVX.zip",
      "label": "",
      "uploader": {
        "login": "SirKnightly",
        "id": 20561911,
        "avatar_url": "https://avatars1.githubusercontent.com/u/20561911?v=4",
        "gravatar_id": "",
        "url": "https://api.github.com/users/SirKnightly",
        "html_url": "https://github.com/SirKnightly",
        "followers_url": "https://api.github.com/users/SirKnightly/followers",
        "following_url": "https://api.github.com/users/SirKnightly/following{/other_user}",
        "gists_url": "https://api.github.com/users/SirKnightly/gists{/gist_id}",
        "starred_url": "https://api.github.com/users/SirKnightly/starred{/owner}{/repo}",
        "subscriptions_url": "https://api.github.com/users/SirKnightly/subscriptions",
        "organizations_url": "https://api.github.com/users/SirKnightly/orgs",
        "repos_url": "https://api.github.com/users/SirKnightly/repos",
        "events_url": "https://api.github.com/users/SirKnightly/events{/privacy}",
        "received_events_url": "https://api.github.com/users/SirKnightly/received_events",
        "type": "User",
        "site_admin": false
      },
      "content_type": "application/octet-stream",
      "state": "uploaded",
      "size": 23138517,
      "download_count": 38,
      "created_at": "2017-07-11T17:49:48Z",
      "updated_at": "2017-07-11T17:49:49Z",
      "browser_download_url": "https://github.com/test/test/releases/download/release_test/fs2_open_test-builds-Win64-AVX.zip"
    },
    {
      "url": "https://api.github.com/repos/test/test/releases/assets/4304185",
      "id": 4304185,
      "name": "fs2_open_test-builds-Win64.zip",
      "label": "",
      "uploader": {
        "login": "SirKnightly",
        "id": 20561911,
        "avatar_url": "https://avatars1.githubusercontent.com/u/20561911?v=4",
        "gravatar_id": "",
        "url": "https://api.github.com/users/SirKnightly",
        "html_url": "https://github.com/SirKnightly",
        "followers_url": "https://api.github.com/users/SirKnightly/followers",
        "following_url": "https://api.github.com/users/SirKnightly/following{/other_user}",
        "gists_url": "https://api.github.com/users/SirKnightly/gists{/gist_id}",
        "starred_url": "https://api.github.com/users/SirKnightly/starred{/owner}{/repo}",
        "subscriptions_url": "https://api.github.com/users/SirKnightly/subscriptions",
        "organizations_url": "https://api.github.com/users/SirKnightly/orgs",
        "repos_url": "https://api.github.com/users/SirKnightly/repos",
        "events_url": "https://api.github.com/users/SirKnightly/events{/privacy}",
        "received_events_url": "https://api.github.com/users/SirKnightly/received_events",
        "type": "User",
        "site_admin": false
      },
      "content_type": "application/octet-stream",
      "state": "uploaded",
      "size": 23161687,
      "download_count": 188,
      "created_at": "2017-07-11T17:33:07Z",
      "updated_at": "2017-07-11T17:33:10Z",
      "browser_download_url": "https://github.com/test/test/releases/download/release_test/fs2_open_test-builds-Win64.zip"
    },
    {
      "url": "https://api.github.com/repos/test/test/releases/assets/4304187",
      "id": 4304185,
      "name": "fs2_open_test-source-Unix.tar.gz",
      "label": "",
      "uploader": {
        "login": "SirKnightly",
        "id": 20561911,
        "avatar_url": "https://avatars1.githubusercontent.com/u/20561911?v=4",
        "gravatar_id": "",
        "url": "https://api.github.com/users/SirKnightly",
        "html_url": "https://github.com/SirKnightly",
        "followers_url": "https://api.github.com/users/SirKnightly/followers",
        "following_url": "https://api.github.com/users/SirKnightly/following{/other_user}",
        "gists_url": "https://api.github.com/users/SirKnightly/gists{/gist_id}",
        "starred_url": "https://api.github.com/users/SirKnightly/starred{/owner}{/repo}",
        "subscriptions_url": "https://api.github.com/users/SirKnightly/subscriptions",
        "organizations_url": "https://api.github.com/users/SirKnightly/orgs",
        "repos_url": "https://api.github.com/users/SirKnightly/repos",
        "events_url": "https://api.github.com/users/SirKnightly/events{/privacy}",
        "received_events_url": "https://api.github.com/users/SirKnightly/received_events",
        "type": "User",
        "site_admin": false
      },
      "content_type": "application/octet-stream",
      "state": "uploaded",
      "size": 23161687,
      "download_count": 188,
      "created_at": "2017-07-11T17:33:07Z",
      "updated_at": "2017-07-11T17:33:10Z",
      "browser_download_url": "https://github.com/test/test/releases/download/release_test/fs2_open_test-source-Unix.tar.gz"
    },
    {
      "url": "https://api.github.com/repos/test/test/releases/assets/4304188",
      "id": 4304185,
      "name": "fs2_open_test-source-Win.zip",
      "label": "",
      "uploader": {
        "login": "SirKnightly",
        "id": 20561911,
        "avatar_url": "https://avatars1.githubusercontent.com/u/20561911?v=4",
        "gravatar_id": "",
        "url": "https://api.github.com/users/SirKnightly",
        "html_url": "https://github.com/SirKnightly",
        "followers_url": "https://api.github.com/users/SirKnightly/followers",
        "following_url": "https://api.github.com/users/SirKnightly/following{/other_user}",
        "gists_url": "https://api.github.com/users/SirKnightly/gists{/gist_id}",
        "starred_url": "https://api.github.com/users/SirKnightly/starred{/owner}{/repo}",
        "subscriptions_url": "https://api.github.com/users/SirKnightly/subscriptions",
        "organizations_url": "https://api.github.com/users/SirKnightly/orgs",
        "repos_url": "https://api.github.com/users/SirKnightly/repos",
        "events_url": "https://api.github.com/users/SirKnightly/events{/privacy}",
        "received_events_url": "https://api.github.com/users/SirKnightly/received_events",
        "type": "User",
        "site_admin": false
      },
      "content_type": "application/octet-stream",
      "state": "uploaded",
      "size": 23161687,
      "download_count": 188,
      "created_at": "2017-07-11T17:33:07Z",
      "updated_at": "2017-07-11T17:33:10Z",
      "browser_download_url": "https://github.com/test/test/releases/download/release_test/fs2_open_test-source-Win.zip"
    }
  ],
  "tarball_url": "https://api.github.com/repos/test/test/tarball/release_test",
  "zipball_url": "https://api.github.com/repos/test/test/zipball/release_test",
  "body": null
}
"""


class GithubTestCase(unittest.TestCase):
    @requests_mock.mock()
    def test_file_listing(self, m):
        m.get("https://api.github.com/repos/test/test/releases/tags/release_test", text=TEST_API_DATA,
              request_headers={
                  "Accept": "application/vnd.github.v3+json"
              },
              headers={
                  "Content-Type": "application/json; charset=utf-8"
              })

        test_config = {
            "github": {
                "user": "test",
                "repo": "test"
            }
        }

        binaries, sources = github.get_release_files("release_test", test_config)

        self.assertEqual(len(binaries), 6)
        self.assertEqual(len(sources), 2)


if __name__ == '__main__':
    unittest.main()
