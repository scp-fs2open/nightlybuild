
<%def name="build(file)">[url=${file.url}]${file.filename}[/url]</%def>

[b]It's finally here![/b]

With this release we decided to drop the "3.Major_revision.Minor_revision" versioning scheme in favor of a year based scheme since the Major and Minor versions did not have much meaning anymore. Instead the scheme will now be "<year>.<number that is incremented every release>.0". The last 0 is still there because some of our systems expect that. It will be gone at some point.

[b]Change log:[/b] (chronologically ordered)
[list]
[li]Various OpenGL optimizations for better graphics performance:
[list]
[li]Animations now use texture arrays[/li]
[li]Model uniforms get sent to the GPU using uniform buffers for less overhead[/li]
[li]Various other, minor changes/li]
[/list]
[/li]
[li]After just 17 years, [b]full Unicode text support[/b]! You can finally use non-ASCII characters without having to worry about special fonts and special characters. This is an opt-in mod flag.[/li]
[li]Added various translation features for making it easier to only distribute one version of a mod which includes all languages.[/li]
[li]OpenAL Soft is included by default in binary distributions of FSO now.[/li]
[li]Added system for dynamically adding new SEXPs. With this a Lua script can expose functionality to the mission which can be used exactly the same as a standard SEXP with all the usual editing features in FRED.[/li]
[li]Replaced Blinn-Phong BRDF with GGX BRDF[/li]
[li]Added support for displaying decals on the surface of an object.[/li]
[li]Refactored bitmap slot handling and removed the fixed upper limit on the number of bitmaps. No more bmpman corruption![/li]
[li]Exposed the movie player to the scripting API for advanced display features[/li]
[li]Integrated support for the Discord Rich Presence API[/li]
[li]Added new, markup based user interface system using libRocket.[/li]
[li]Converted pilot files from custom binary format to JSON[/li]
[/list]


Launchers, if you don't have one already:
[b]All platforms: [/b] For every day use, we recommend [url=https://www.hard-light.net/forums/index.php?topic=94068.0]Knossos[/url], an integrated solution for downloading and launching mods.

[hidden=Alternative Launchers]
Cross-platform: [url=http://www.hard-light.net/forums/index.php?topic=89162]wxLauncher 0.12.x Test Build[/url] (ongoing project for a unified launcher, you should upgrade to the latest RC/test build if you have not yet)
[b]Important:[/b] For best compatibility with FSO 3.8 and later you should use at least wxLauncher 0.12.

Windows:  [url=http://scp.fsmods.net/files/Launcher55g.zip]Launcher 5.5g[/url] ([url=http://scp.indiegames.us/builds/Launcher55g.zip]Mirror[/url]) ([url=http://www.mediafire.com/?wdvzn7hhhzh418m]Mirror[/url]) Not compatible with Windows 8+, use wxLauncher above
OS X:  Soulstorm's [url=http://www.hard-light.net/forums/index.php/topic,51391.0.html]OS X Launcher 3.0[/url]
Linux:  [url=http://www.hard-light.net/forums/index.php/topic,53206.0.html]YAL[/url] or [url=http://www.hard-light.net/wiki/index.php/Fs2_open_on_Linux/Graphics_Settings]by hand[/url] or whatever you can figure out.[/hidden]

[img]http://scp.indiegames.us/img/windows-icon.png[/img] [color=green][size=12pt]Windows (32/64-bit)[/size][/color]
[size=8pt]Compiled by [url=http://www.appveyor.com/]Appveyor[/url] on Windows Server 2012 R2 64-bit, Visual Studio Community 2015 with Update 3[/size]

[b]64-bit:[/b] ${build(groups["Win64"].mainFile)}

[b]32-bit:[/b] ${build(groups["Win32"].mainFile)}
[size=8pt]This one is based on the SSE2 Optimizations from the MSVC Compiler.[/size]

[hidden=Alternative builds]

[b]64-bit AVX:[/b] ${build(groups["Win64"].subFiles["AVX"])}
[size=8pt]This one is based on the AVX Optimizations from the MSVC Compiler (fastest build if your CPU supports AVX instructions).[/size]


[b]32-bit AVX:[/b] ${build(groups["Win32"].subFiles["AVX"])}
[size=8pt]This one is based on the AVX Optimizations from the MSVC Compiler.[/size]

[b]What are those SSE, SSE2 and AVX builds I keep seeing everywhere?[/b]
[url=http://www.hard-light.net/forums/index.php?topic=65628.0]Your answer is in this topic.[/url]
Don't want to deal with that? Use [url=https://www.hard-light.net/forums/index.php?topic=94068.0]Knossos[/url] and it will download the best build specifically for your PC!
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
[url=${sources["Unix"].url}]Source Code (Unix line endings)[/url]

[url=${sources["Win"].url}]Source Code (Windows line endings)[/url]
[/hidden]

[hidden=TrackIR Users]
[size=12pt]Important!![/size]
An external DLL is required for FSO to use TrackIR functions.  The following DLL is simply unpacked in to your main FreeSpace2 root dir.
TrackIR is only supported on Windows.
[url=http://www.mediafire.com/download.php?4zw024zrh44etse]TrackIR SCP DLL[/url] ([url=http://scp.fsmods.net/builds/scptrackir.zip]Mirror[/url]) ([url=http://scp.indiegames.us/builds/scptrackir.zip]Mirror[/url])[/hidden]

Known issues:
[list]
[li][url=https://github.com/scp-fs2open/fs2open.github.com/issues]Github issues[/url] and [url=https://github.com/scp-fs2open/fs2open.github.com/pulls]pending pull requests[/url][/li]
[li]See the list of [url=http://scp.indiegames.us/mantis/search.php?project_id=1&status_id%5B%5D=10&status_id%5B%5D=20&status_id%5B%5D=30&status_id%5B%5D=40&status_id%5B%5D=50&priority_id%5B%5D=40&priority_id%5B%5D=50&priority_id%5B%5D=60&sticky_issues=on&sortby=last_updated&dir=DESC&per_page=200&hide_status_id=-2]Fix for next release[/url] bugs - mark a bug as an elevated priority (high, urgent, immediate) to get it included in that filter.[/li]
[/list]
