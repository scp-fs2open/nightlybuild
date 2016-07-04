
${message}

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
[li]Here is the filter for [url=http://scp.indiegames.us/mantis/search.php?project_id=1&status_id%5B%5D=10&status_id%5B%5D=20&status_id%5B%5D=30&status_id%5B%5D=40&status_id%5B%5D=50&status_id%5B%5D=60&sticky_issues=on&target_version=3.7.4&sortby=last_updated&dir=DESC&hide_status_id=-2]Target 3.7.4[/url] bugs.[/li]
[/list]


[img]http://scp.indiegames.us/img/windows-icon.png[/img] [color=green][size=12pt]Windows[/size][/color]
[size=8pt]Compiled by [url=http://www.appveyor.com/]Appveyor[/url] on Windows Server 2012 R2 64-bit, Visual Studio Community 2015 with Update 3[/size]

[url=http://scp.fsmods.net/builds/WIN/fs2_open_3.7.4_RC2.7z]fs2_open_3.7.4_RC2.7z[/url] ([url=http://scp.indiegames.us/builds/WIN/fs2_open_3.7.4_RC2.7z]Mirror[/url]) ([color=yellow][url=http://scp.fsmods.net/builds/WIN/fs2_open_3.7.4_RC2.md5]MD5[/url][/color])
[size=8pt]This one is based on the SSE2 Optimizations from the MSVC Compiler.[/size]

[hidden=Alternative builds]
[b]If you don't know which one to get, get the third one (no SSE).[/b]  [color=red]If you don't know what SSE means, read this: http://en.wikipedia.org/wiki/Streaming_SIMD_Extensions[/color]
You can use freely available tools like [url=http://www.cpuid.com/softwares/cpu-z.html]CPU-Z[/url] to check which SSE capabilities your CPU has.

[url=http://scp.fsmods.net/builds/WIN/fs2_open_3.7.4_RC2_AVX.7z]fs2_open_3.7.4_RC2_AVX.7z[/url] ([url=http://scp.indiegames.us/builds/WIN/fs2_open_3.7.4_RC2_AVX.7z]Mirror[/url]) ([color=yellow][url=http://scp.fsmods.net/builds/WIN/fs2_open_3.7.4_RC2_AVX.md5]MD5[/url][/color])
[size=8pt]This one is based on the AVX Optimizations from the MSVC Compiler (fastest build if your CPU supports AVX instructions).[/size]

[url=http://scp.fsmods.net/builds/WIN/fs2_open_3.7.4_RC2_SSE.7z]fs2_open_3.7.4_RC2_SSE.7z[/url] ([url=http://scp.indiegames.us/builds/WIN/fs2_open_3.7.4_RC2_SSE.7z]Mirror[/url]) ([color=yellow][url=http://scp.fsmods.net/builds/WIN/fs2_open_3.7.4_RC2_SSE.md5]MD5[/url][/color])
[size=8pt]This one is based on the SSE Optimizations from the MSVC Compiler.[/size]

[url=http://scp.fsmods.net/builds/WIN/fs2_open_3.7.4_RC2_NO-SSE.7z]fs2_open_3.7.4_RC2_NO-SSE.7z[/url] ([url=http://scp.indiegames.us/builds/WIN/fs2_open_3.7.4_RC2_NO-SSE.7z]Mirror[/url]) ([color=yellow][url=http://scp.fsmods.net/builds/WIN/fs2_open_3.7.4_RC2_NO-SSE.md5]MD5[/url][/color])

[b]What are those SSE and SSE2 builds I keep seeing everywhere?[/b]
[url=http://www.hard-light.net/forums/index.php?topic=65628.0]Your answer is in this topic.[/url]
[/hidden]


[img]http://scp.indiegames.us/img/mac-icon.png[/img] [color=green][size=12pt]OS X Universal (32/64-bit Intel)[/size][/color]
[size=8pt]Compiled on OS X 10.11.4, Xcode 7.3 ([url=https://gist.github.com/yamaya/2924292]Apple LLVM version cross-reference[/url])[/size]

[url=http://scp.fsmods.net/builds/OSX/fs2_open_3.7.4_RC2.dmg]fs2_open_3.7.4_RC2.dmg[/url] ([url=http://scp.indiegames.us/builds/OSX/fs2_open_3.7.4_RC2.dmg]Mirror[/url]) ([color=yellow][url=http://scp.fsmods.net/builds/OSX/fs2_open_3.7.4_RC2.md5]MD5[/url][/color])


[hidden=Other Platforms, Source Code]
[img]http://scp.indiegames.us/img/linux-icon.png[/img] [color=green][size=12pt]Ubuntu Linux 32-bit[/size][/color]
[size=8pt]Compiled on Ubuntu 14.04.4 LTS 32-bit, GCC 4.8.4[/size]
The Ubuntu builds are built and provided as a reference, and also because Ubuntu is a very common Desktop Linux distribution.  We usually recommend Linux users compile their own builds, but if you happen to be running 32-bit Ubuntu, or 64-bit Ubuntu with 32-bit libraries installed, these may work fine for you.  There have been reports of package managers maintaining FSO packages in various Linux distributions, if you plan to package an FSO release for a distribution please let use know and we will include a reference to it in our release posts.

[url=http://scp.fsmods.net/builds/LINUX/fs2_open_3.7.4_RC2.tar.bz2]fs2_open_3.7.4_RC2.tar.bz2[/url] ([url=http://scp.indiegames.us/builds/LINUX/fs2_open_3.7.4_RC2.tar.bz2]Mirror[/url]) ([color=yellow][url=http://scp.fsmods.net/builds/LINUX/fs2_open_3.7.4_RC2.md5]MD5[/url][/color])


[img]http://scp.indiegames.us/img/freebsd-icon.png[/img] [color=green][size=12pt]FreeBSD 64-bit (experimental, limited support)[/size][/color]
[size=8pt]Compiled on PCBSD 10.2 64-bit, clang 3.4.1[/size]
As FreeBSD is still a small player in the desktop space, but PC-BSD is becoming a much more user-friendly platform, we were able to get it reliably working with our build system.  The limited user base for these builds will likely keep them in the experimental realm, so if you do have any issues or successes with them, please report your experiences here.

[url=http://scp.fsmods.net/builds/FREEBSD/fs2_open_3.7.4_RC2.tar.bz2]fs2_open_3.7.4_RC2.tar.bz2[/url] ([url=http://scp.indiegames.us/builds/FREEBSD/fs2_open_3.7.4_RC2.tar.bz2]Mirror[/url]) ([color=yellow][url=http://scp.fsmods.net/builds/FREEBSD/fs2_open_3.7.4_RC2.md5]MD5[/url][/color])

[color=green][size=12pt]Source Code Export[/size][/color] ([color=yellow][url=http://scp.fsmods.net/builds/fs2_open_3_7_4_RC2_src.md5]MD5[/url][/color])
[url=http://scp.fsmods.net/builds/fs2_open_3_7_4_RC2_src.tgz]fs2_open_3_7_4_RC2_src.tgz[/url] ([url=http://scp.indiegames.us/builds/fs2_open_3_7_4_RC2_src.tgz]Mirror[/url])
[/hidden]