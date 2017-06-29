
<%def name="build(file)">[url=${file.url}]${file.filename}[/url]</%def>

[b]Major changes in this version:[/b] (chronologically ordered)
[list]
[li][i]Support for APNG animations:[/i] [url=https://en.wikipedia.org/wiki/APNG]APNG[/url] is a variant of the established PNG format which allows to store animations instead of single frames in a PNG file. This change allows to use these animation files in FSO which significantly improves usability for modders since they no longer have to store all individual frames as separate images.[/li]
[li][i]Physically-Based Rendering (PBR)[/i]: This upgrade of our rendering engine allows to use [url=https://en.wikipedia.org/wiki/Physically_based_rendering]PBR[/url] assets to make models look more realistic and allow more artistic freedom for modders since they have more control over how a model looks. This also added support for HDR lighting which should improve the overall graphics experience.[/li]
[li][i]SDL2 usage on all platforms[/i]: SDL is a library for abstracting away the differences between different platforms. We now use SDL2 for all platforms which reduces the amount of platform-specific code tremendously and should result in better usability on all platforms. This was a major change that has been in development for several years. Here are a few key features that were added:
[list]
[li]Pilot and configuration data is now stored in the correct location across all platforms (this allows to run FSO on Windows from the Program Files directory without administrator rights)[/li]
[li]All platforms now use the ini files for storing settings. This fixes a lot of issues with the registry on Windows.[/li]
[li]Better support for input devices. Since SDL handles keyboard, mouse and joystick input we now have better support on newer OS versions. [b]Note:[/b] This does not mean that we support multiple joysticks (yet). There is ongoing development effort to support this but this release does not have that yet.[/li]
[/list]
[/li]
[li][i]CMake build system generation:[/i] This isn't relevant for players but we are now using [url=https://en.wikipedia.org/wiki/CMake]CMake[/url] for handling compiling our builds. This improves cross-platform support and allows to implement advanced compilation features across multiple platforms. Modders will like the new "FastDebug" builds which are like the previous "Debug" builds but are compiled with all the optimizations of normal Release builds. That should make modding a lot easier since you can now debug your mod with almost the same performance as a Release build.[/li]
[li][i]Improved shield effects:[/i] Rendering of the shields is now handled by special shaders which improves the overall quality of the effects and allows more freedom for future effects.[/li]
[li][i]Native particle systems:[/i] Particles have always been supported by FSO but the effects that could be created by them were very limited. There were some attempts to fix this by using Lua scripting for more advanced features but that suffered from performance issues. With these new particle systems that feature has been integrated directly into the engine which should improve performance and allow for better effects in the future.[/li]
[li][i]TrueType Font support:[/i] [url=https://en.wikipedia.org/wiki/TrueType]TrueType[/url] fonts improve the text rendering capabilities of FSO by allowing to use freely scaleable font faces instead of the previous bitmap fonts.[/li]
[li][i]Use OpenGL Core Profile for rendering:[/i] This is another major graphical upgrade which adds support for the OpenGL Core profile across all platforms (this was also made possible by the SDL2 integration). This upgrade allows us to use more modern rendering techniques and is especially useful for our Linux users who use the open-source Mesa drivers since our shaders failed to compile with those drivers. Now everyone will be able to enjoy the new graphical features added in this and previous releases. This also made some internal changes to how we handle rendering which improves the usability of our rendering engine within our code.[/li]
[li][i]Use FFmpeg for video & audio decoding:[/i] [url=https://www.ffmpeg.org/]FFmpeg[/url] is a multi-media library which exposes functionality for decoding video and audio files to their raw form so that we can use that data. Thanks to this library we can now play 1080p cutscenes without any stuttering or frame-timing issues. It also allows to use more advanced audio and video codecs such as H.264 for video or Opus for audio.[/li]
[/list]
This list is taken from our [url=https://github.com/scp-fs2open/fs2open.github.com/wiki/History-and-Release-Timeline]GitHub wiki[/url].


[size=12pt]Important!![/size]
As always, you need OpenAL installed.  Linux and OS X come with it but Windows users will need to get Creative's [url=http://scp.indiegames.us/builds/oalinst.zip]OpenAL installer[/url]. Alternatively, if Creative's OpenAL doesn't work with your hardware, you can use [url=http://kcat.strangesoft.net/openal.html#download]OpenAL Soft[/url].

[hidden=TrackIR Users]
[size=12pt]Important!![/size]
An external DLL is required for FSO to use TrackIR functions.  The following DLL is simply unpacked in to your main FreeSpace2 root dir.
TrackIR is only supported on Windows.
[url=http://www.mediafire.com/download.php?4zw024zrh44etse]TrackIR SCP DLL[/url] ([url=http://scp.fsmods.net/builds/scptrackir.zip]Mirror[/url]) ([url=http://scp.indiegames.us/builds/scptrackir.zip]Mirror[/url])[/hidden]

Launchers, if you don't have one already:
All platforms:  [url=http://www.hard-light.net/forums/index.php?topic=89162]wxLauncher 0.12.x Test Build[/url] (ongoing project for a unified launcher, you should upgrade to the latest RC/test build if you have not yet)
[b]Important:[/b] For best compatibility with FSO 3.8 you should use at least wxLauncher 0.12.

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
[color=red][b]WARNING:[/b][/color] 64-bit builds are still experimental. These builds have been tested but there may still be issues that are not present in the 32-bit builds. Make sure you read the installation instructions below.
[b]Installation:[/b] If you use the 64-bit executables you have to make sure that you install all files from the zip file and that there are no remaining 32-bit DLLs left in your FSO directory. Some users have installed the 32-bit OpenAL DLLs directly into your FSO directory which is a common cause for errors. If the launcher fails to use the 64-bit executable this is the first thing you should check.

[hidden=Alternative builds]

[b]32-bit AVX:[/b] ${build(groups["Win32"].subFiles["AVX"])}
[size=8pt]This one is based on the AVX Optimizations from the MSVC Compiler (fastest build if your CPU supports AVX instructions).[/size]

[b]64-bit AVX:[/b] ${build(groups["Win64"].subFiles["AVX"])}
[color=red][b]WARNING:[/b][/color] 64-bit builds are still experimental.
[size=8pt]This one is based on the AVX Optimizations from the MSVC Compiler.[/size]

[b]What are those SSE, SSE2 and AVX builds I keep seeing everywhere?[/b]
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