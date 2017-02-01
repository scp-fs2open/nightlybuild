
<%def name="build(file)">[url=${file.url}]${file.filename}[/url]</%def>

[size=12pt]Important!![/size]
As always, you need OpenAL installed.  Linux and OS X come with it but Windows users will need to get Creative's [url=http://scp.indiegames.us/builds/oalinst.zip]OpenAL installer[/url]. Alternatively, if Creative's OpenAL doesn't work with your hardware, you can use [url=http://kcat.strangesoft.net/openal.html#download]OpenAL Soft[/url].

[hidden=TrackIR Users]
[size=12pt]Important!![/size]
An external DLL is required for FSO to use TrackIR functions.  The following DLL is simply unpacked in to your main FreeSpace2 root dir.
TrackIR is only supported on Windows.
[url=http://www.mediafire.com/download.php?ihzkihqj2ky]TrackIR SCP DLL[/url] ([url=http://scp.fsmods.net/builds/scptrackir.zip]Mirror[/url]) ([url=http://scp.indiegames.us/builds/scptrackir.zip]Mirror[/url])[/hidden]

Launchers, if you don't have one already:
All platforms:  [url=http://www.hard-light.net/forums/index.php?topic=67950.0]wxLauncher[/url] (ongoing project for a unified launcher)

[hidden=Alternative Launchers]
Windows:  [url=http://scp.fsmods.net/files/Launcher55g.zip]Launcher 5.5g[/url] ([url=http://scp.indiegames.us/builds/Launcher55g.zip]Mirror[/url]) ([url=http://www.mediafire.com/?wdvzn7hhhzh418m]Mirror[/url]) Not compatible with Windows 8+, use wxLauncher above
OS X:  Soulstorm's [url=http://www.hard-light.net/forums/index.php/topic,51391.0.html]OS X Launcher 3.0[/url]
Linux:  [url=http://www.hard-light.net/forums/index.php/topic,53206.0.html]YAL[/url] or [url=http://www.hard-light.net/wiki/index.php/Fs2_open_on_Linux/Graphics_Settings]by hand[/url] or whatever you can figure out.[/hidden]

Known issues:
[list]
[li][url=https://github.com/scp-fs2open/fs2open.github.com/issues]Github issues[/url] and [url=https://github.com/scp-fs2open/fs2open.github.com/pulls]pending pull requests[/url][/li]
[li]See the list of [url=http://scp.indiegames.us/mantis/search.php?project_id=1&status_id%5B%5D=10&status_id%5B%5D=20&status_id%5B%5D=30&status_id%5B%5D=40&status_id%5B%5D=50&priority_id%5B%5D=40&priority_id%5B%5D=50&priority_id%5B%5D=60&sticky_issues=on&sortby=last_updated&dir=DESC&per_page=200&hide_status_id=-2]Fix for next release[/url] bugs - mark a bug as an elevated priority (high, urgent, immediate) to get it included in that filter.[/li]
[/list]


[img]http://scp.indiegames.us/img/windows-icon.png[/img] [color=green][size=12pt]Windows (32/64-bit)[/size][/color]
[size=8pt]Compiled by [url=http://www.appveyor.com/]Appveyor[/url] on Windows Server 2012 R2 64-bit, Visual Studio Community 2015 with Update 3[/size]

[b]32-bit:[/b] ${build(groups["Win32"].mainFile)}
[size=8pt]This one is based on the SSE2 Optimizations from the MSVC Compiler.[/size]

[b]64-bit:[/b] ${build(groups["Win64"].mainFile)}
[color=red][b]WARNING:[/b][/color] 64-bit builds are still experimental.

[hidden=Alternative builds]

[b]32-bit AVX:[/b] ${build(groups["Win32"].subFiles["AVX"])}
[size=8pt]This one is based on the AVX Optimizations from the MSVC Compiler (fastest build if your CPU supports AVX instructions).[/size]

[b]64-bit AVX:[/b] ${build(groups["Win64"].subFiles["AVX"])}
[color=red][b]WARNING:[/b][/color] 64-bit builds are still experimental.
[size=8pt]This one is based on the AVX Optimizations from the MSVC Compiler.[/size]

[b]What are those SSE and SSE2 builds I keep seeing everywhere?[/b]
[url=http://www.hard-light.net/forums/index.php?topic=65628.0]Your answer is in this topic.[/url]
[/hidden]


[img]http://scp.indiegames.us/img/mac-icon.png[/img] [color=green][size=12pt]OS X Universal (32/64-bit Intel)[/size][/color]
[size=8pt]Compiled on OS X 10.11.4, Xcode 7.3 ([url=https://gist.github.com/yamaya/2924292]Apple LLVM version cross-reference[/url])[/size]

${build(groups["MacOSX"].mainFile)}

[img]http://scp.indiegames.us/img/linux-icon.png[/img] [color=green][size=12pt]Linux 64-bit[/size][/color]
[size=8pt]Compiled on Ubuntu 14.04.4 LTS 64-bit, GCC 5[/size]
${build(groups["Linux"].mainFile)}

These builds use a mechanism called [url=http://appimage.org/]AppImage[/url] which should allow these builds to run on most Linux distributions. However, we recommend that you compile your own builds which will result in less issues.
Alternatively, if there is a package in your software repository then you should use that. If you are the maintainer of such a package for a distribution then let us know and we will include that here.

[hidden=Other Platforms, Source Code]
[color=green][size=12pt]Source Code Export[/size][/color]
[url=${groups["Win32"].mainFile.tarball}]Source Code[/url]
[/hidden]