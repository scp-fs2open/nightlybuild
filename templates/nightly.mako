Here is the nightly for ${date} - Revision ${revision}

% for file in files:

Group: ${file["group"]}
[url=${file["url"]}]${file["name"]}[/url]
SHA1: ${file["sha1"]}

% endfor

[code]
${log}
[/code]