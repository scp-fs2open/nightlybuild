<%def name="extra_files(platform)">
URL
http://www.fsoinstaller.com/files/installer/java/
mod.ini
FS2.bmp
    %if platform == "Win32" or platform == "Win64":
MULTIURL
http://scp.fsmods.net/builds/
http://scp.indiegames.us/builds/
ENDMULTI
scptrackir.zip
HASH
MD5
scptrackir.dll
72a16493f2eccd6e2e389d53e076780b
HASH
MD5
scptrackir64.dll
044def803cb9795bdc55c6e4e6b619f0
    %endif
</%def>

<%def name="sub_group(file)">\
% if file.subgroup is not None:
${file.subgroup}\
%else:
Standard\
% endif
</%def>

<%def name="build(platform, file)">
NAME
FreeSpace Open ${version} ${platform} ${sub_group(file)}
DESC
${platform} builds for FreeSpace 2 Open.\
    % if file.subgroup is not None:
 Compiled with ${file.subgroup} optimizations.
ENDDESC
    %else:

ENDDESC
    % endif
FOLDER
/
URL
${file.base_url}
${file.filename}
    % for filename, hash in file.content_hashes:
HASH
SHA-256
${filename}
${hash}
    % endfor
${extra_files(platform)}
VERSION
${version}
END
</%def>

% for platform, group in groups.items():

${build(platform, group.mainFile)}

    %for name, subfile in group.subFiles.items():
${build(platform, subfile)}
    %endfor

% endfor