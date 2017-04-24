Here is the nightly for ${date} - Revision ${revision}

% if not success:
[b][color=red]At least one of the nightly builds failed![/color][/b]
% endif

% for file in files:

Group: ${file.group}
[url=${file.url}]${file.name}[/url]
SHA1: ${file.sha1}

% endfor

Download hosting is provided by [url=https://bintray.com/]JFrog Bintray[/url].

[code]
${log}
[/code]