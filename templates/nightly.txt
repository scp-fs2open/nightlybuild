This is a test for [url=http://www.hard-light.net/forums/index.php?topic=92035.msg1822672#new]my nightly script[/url], please ignore.

Here is the nightly for ${date} - Revision ${revision}

% for file in files:

Group: ${file["group"]}
[url=${file["url"]}]${file["name"]}[/url]
SHA1: ${file["sha1"]}

% endfor

[code]
${log}
[/code]