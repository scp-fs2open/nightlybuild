import unittest
import requests_mock

FILE_LISTING = '''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">
<html>
 <head>
  <title>Index of /builds/nightly/test_tag</title>
 </head>
 <body>
<h1>Index of /builds/nightly/test_tag</h1>
  <table>
   <tr><th valign="top"><img src="/icons/blank.gif" alt="[ICO]"></th><th><a href="?C=N;O=D">Name</a></th><th><a href="?C=M;O=A">Last modified</a></th><th><a href="?C=S;O=A">Size</a></th><th><a href="?C=D;O=A">Description</a></th></tr>
   <tr><th colspan="5"><hr></th></tr>
<tr><td valign="top"><img src="/icons/back.gif" alt="[PARENTDIR]"></td><td><a href="/builds/nightly/">Parent Directory</a></td><td>&nbsp;</td><td align="right">  - </td><td>&nbsp;</td></tr>
<tr><td valign="top"><img src="/icons/compressed.gif" alt="[   ]"></td><td><a href="nightly_test_tag-builds-Linux.tar.gz">nightly_test_tag-builds-Linux.tar.gz</a></td><td align="right">2023-04-13 06:25  </td><td align="right"> 30M</td><td>&nbsp;</td></tr>
<tr><td valign="top"><img src="/icons/compressed.gif" alt="[   ]"></td><td><a href="nightly_test_tag-builds-MacOSX.tar.gz">nightly_test_tag-builds-MacOSX.tar.gz</a></td><td align="right">2023-04-13 06:24  </td><td align="right"> 17M</td><td>&nbsp;</td></tr>
<tr><td valign="top"><img src="/icons/compressed.gif" alt="[   ]"></td><td><a href="nightly_test_tag-builds-Win32.zip">nightly_test_tag-builds-Win32.zip</a></td><td align="right">2023-04-13 06:43  </td><td align="right"> 29M</td><td>&nbsp;</td></tr>
<tr><td valign="top"><img src="/icons/compressed.gif" alt="[   ]"></td><td><a href="nightly_test_tag-builds-x64.zip">nightly_test_tag-builds-x64.zip</a></td><td align="right">2023-04-13 06:44  </td><td align="right"> 35M</td><td>&nbsp;</td></tr>
<tr><td valign="top"><img src="/icons/unknown.gif" alt="[   ]"></td><td><a href="nightly_test_tag-debug-Win32.7z">nightly_test_tag-debug-Win32.7z</a></td><td align="right">2023-04-13 06:43  </td><td align="right"> 68M</td><td>&nbsp;</td></tr>
<tr><td valign="top"><img src="/icons/unknown.gif" alt="[   ]"></td><td><a href="nightly_test_tag-debug-x64.7z">nightly_test_tag-debug-x64.7z</a></td><td align="right">2023-04-13 06:44  </td><td align="right"> 71M</td><td>&nbsp;</td></tr>
   <tr><th colspan="5"><hr></th></tr>
</table>
<address>Apache/2.4.25 (Debian) Server at datacorder.porphyrion.feralhosting.com Port 80</address>
</body></html>
'''

class NightlyListTestCase(unittest.TestCase):
    @requests_mock.mock()
    def test_file_listing(self, m):
        m.get("http://01.example.org/builds/nightly/test_tag/", text=FILE_LISTING)

        test_config = {
            "ftp": {
                "mirrors": [
                    "http://01.example.org/builds/{type}/{version}/{file}",
                    "http://02.example.org/builds/{type}/{version}/{file}",
                ]
            }
        }

        import file_list
        files = file_list.get_nightly_files("nightly_test_tag", test_config)
        self.assertEqual(4, len(files))


if __name__ == '__main__':
    unittest.main()
