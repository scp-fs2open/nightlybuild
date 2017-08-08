import unittest
from unittest import mock
from unittest.mock import Mock

import ftp


class FtpTestCase(unittest.TestCase):
    @mock.patch("ftp.FTP", autospec=True)
    def test_file_listing(self, MockFTP):
        MockFTP.return_value = Mock()
        mock_ftp_obj = MockFTP()
        mock_ftp_obj.__enter__ = Mock(return_value=mock_ftp_obj)
        mock_ftp_obj.__exit__ = Mock()

        mock_ftp_obj.mlsd = Mock(return_value=[
            (".", {"type": "cdir"}),
            ("..", {"type": "pdir"}),
            ("nightly_test_tag-builds-Linux.tar.gz", {"type": "file"}),
            ("nightly_test_tag-builds-MacOSX.tar.gz", {"type": "file"}),
            ("nightly_test_tag-builds-Win32.zip", {"type": "file"}),
            ("nightly_test_tag-builds-Win64.zip", {"type": "file"}),
        ])
        test_config = {
            "ftp": {
                "host": "example.org",
                "user": "user",
                "pass": "pass",
                "path": "public_html/builds/{type}/{version}/",
                "mirrors": [
                    "http://01.example.org/builds/{type}/{version}/{file}",
                    "http://02.example.org/builds/{type}/{version}/{file}",
                ]
            }
        }
        files = ftp.get_files("nightly", "nightly_test_tag", test_config)
        self.assertEqual(4, len(files))


if __name__ == '__main__':
    unittest.main()
