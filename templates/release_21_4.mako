
<%def name="build(file)">[url=${file.url}]${file.filename}[/url]</%def>

Please note: I'll clean this up in the next 24 hours. These changes need to be grouped (i.e. scripting, FRED, ...) to make this list less overwhelming. --ngld

[b]Change log:[/b] (chronologically ordered)
[list]
[li][url=https://github.com/scp-fs2open/fs2open.github.com/pull/3494]changed ship turnrate when following waypoints to fix a bug introduced in 20.2[/url][/li]
[li][url=https://github.com/scp-fs2open/fs2open.github.com/pull/3467]Ai_aims_from_center flag fixed (the flag didn't actually affect aiming)[/url][/li]
[li][url=https://github.com/scp-fs2open/fs2open.github.com/pull/3455]glowpoint depth removed (the depth made it possible to position the glowpoint above the hull which looked awkward)[/url][/li]
[li][url=https://github.com/scp-fs2open/fs2open.github.com/pull/3461]added [font=Courier]$Homing Auto-Target Method:[/font] to weapons which changes heatseekers to targett a random enemy instead of the closest[/url][/li]
[li][url=https://github.com/scp-fs2open/fs2open.github.com/pull/3466]added the [font=Courier]no collide[/font] flag for weapons which allows a modder to disable collision for specific weapons[/url][/li]
[li][url=https://github.com/scp-fs2open/fs2open.github.com/pull/3476]added Lua functions to control sounds assigned to objects (assignSound, removeSoundByIndex and removeSound)[/url][/li]
[li][url=https://github.com/scp-fs2open/fs2open.github.com/pull/3060]added [font=Courier]ai_profiles.tbl[/font] flag [font=Courier]$AI secondary range awareness:[/font] which can be set to [font=Courier]aware[/font] to change AI behavior to only select secondary weapons that are in range of the AI's target[/url][/li]
[li][url=https://github.com/scp-fs2open/fs2open.github.com/pull/3477]fixed collision checks involving accelerating weapons (the check happened to late potentially missing collisions)[/url][/li]
[li][url=https://github.com/scp-fs2open/fs2open.github.com/pull/3448]fixed a bug where full shields were occasionally pierced (you'll have to enable [font=Courier]$fixed ship-weapon collisions:[/font] in [font=Courier]ai_profiles.tbl[/font] or set your target version to 21.4 to get the new behavior because this fix might break mission balance)[/url][/li]
[li][url=https://github.com/scp-fs2open/fs2open.github.com/pull/3481]fixed APNG misc mainhall animations (the engine only used one random animation per group instead of picking a new animation for each loop)[/url][/li]
[li][url=https://github.com/scp-fs2open/fs2open.github.com/pull/3301]implement [font=Courier]$Substitute:[/font] for beams[/url][/li]
[li][url=https://github.com/scp-fs2open/fs2open.github.com/pull/2817]implemented type 5 beams[/url][/li]
[li][url=https://github.com/scp-fs2open/fs2open.github.com/pull/3480]added [font=Courier]ai_profiles.tbl[/font] flag [font=Courier]$no shield damage from ship collisions:[/font] which causes ship-ship collisions to cause hull damage instead of shield damage to the heavier ship[/url][/li]
[li][url=https://github.com/scp-fs2open/fs2open.github.com/pull/3505]added keyboard shortcut (Ctrl+Shift+S) for "Save As" in FRED[/url][/li]
[li][url=https://github.com/scp-fs2open/fs2open.github.com/pull/3498]fixed an assertion when exiting missions through scripting[/url][/li]
[li][url=https://github.com/scp-fs2open/fs2open.github.com/pull/3499]fixed scripting documentation to correctly display placeholders like [font=Courier]<argument>[/font][/url][/li]
[li][url=https://github.com/scp-fs2open/fs2open.github.com/pull/3496]added Lua function [font=Courier]maybePlayCutscene[/font] to start cutscenes[/url][/li]
[li][url=https://github.com/scp-fs2open/fs2open.github.com/pull/3509]fixed shadows in briefing stages[/url][/li]
[li][url=https://github.com/scp-fs2open/fs2open.github.com/pull/3507]improved nebula poof rendering[/url][/li]
[li][url=https://github.com/scp-fs2open/fs2open.github.com/pull/3514]a negative [font=Courier]$Hull Repair Rate[/font] can now kill the player if their health drops below 0 due to it[/url][/li]
[li][url=https://github.com/scp-fs2open/fs2open.github.com/pull/3511]fixed [font=Courier]+Attenuation:[/font] for beams (the previous implementation didn't have the intended effect and often didn't change the damage at all)[/url][/li]
[li][url=https://github.com/scp-fs2open/fs2open.github.com/pull/3457]added [font=Courier]+Weapon Optimum Range:[/font] for weapons which the AI will attempt to maintain while attacking (this makes it possible to tell the AI to stick close to their target or snipe from afar)[/url][/li]
[li][url=https://github.com/scp-fs2open/fs2open.github.com/pull/3501]added in-game options menu options for lightshafts and bloom[/url][/li]
[li][url=https://github.com/scp-fs2open/fs2open.github.com/pull/3504]fixed single missions in the tech room becoming invisible if their title was translated[/url][/li]
[li][url=https://github.com/scp-fs2open/fs2open.github.com/pull/3064]added [font=Courier]time-to-goal[/font] SEXP which returns the seconds a ship will take to reach its goal[/url][/li]
[li][url=https://github.com/scp-fs2open/fs2open.github.com/pull/3528]added [font=Courier]is-language[/font] SEXP which checks whether the game is currently running in the given language[/url][/li]
[li][url=https://github.com/scp-fs2open/fs2open.github.com/pull/3512]fixed memory leak in F3 lab[/url][/li]
[li][url=https://github.com/scp-fs2open/fs2open.github.com/pull/3441]added ballistic beams[/url][/li]
[li][url=https://github.com/scp-fs2open/fs2open.github.com/pull/3510]added new script options for sounds: OS_PLAY_ON_PLAYER (allows persistent sounds to play on the player's ship) and OS_LOOPING_DISABLED (sound plays only once even if you don't remove it later)[/url][/li]
[li][url=https://github.com/scp-fs2open/fs2open.github.com/pull/3183]fixed AI multilock aiming; the AI now has the same restrictions as the player[/url][/li]
[li][url=https://github.com/scp-fs2open/fs2open.github.com/pull/3529]added [font=Courier]+Shield Regen Hit Delay:[/font] to [font=Courier]ships.tbl[/font] which specifies the delay after a hit before which the shield starts regenerating[/url][/li]
[li][url=https://github.com/scp-fs2open/fs2open.github.com/pull/3545]fixed hang on debug launch if a quotation mark in a string list was missing[/url][/li]
[li][url=https://github.com/scp-fs2open/fs2open.github.com/pull/3531]fixed invalid memory access (possible crash) for model point shields with a single quadrant[/url][/li]
[li][url=https://github.com/scp-fs2open/fs2open.github.com/pull/3555]added [font=Courier]num firepoints for burst shots[/font] burst flag for weapons which sets the amount of shots per burst to the number of firepoints used to fire the weapon[/url][/li]
[li][url=https://github.com/scp-fs2open/fs2open.github.com/pull/3556]added Lua function [font=Courier]setVolume[/font] which allows scripts to change the volume of an audio stream[/url][/li]
[li][url=https://github.com/scp-fs2open/fs2open.github.com/pull/3559]added [font=Courier]game_settings.tbl[/font] setting [font=Courier]$Don't pre-empt training message voice:[/font] which forces the game to finish the training message before it plays further messages (before, new messages would interrupt training messages)[/url][/li]
[li][url=https://github.com/scp-fs2open/fs2open.github.com/pull/3571]added [font=Courier]$Chase View Offset:[/font] and [font=Courier]$Chase View Rigidity:[/font] to [font=Courier]ships.tbl[/font] which allow modders to tweak the chase view for each ship[/url][/li]
[li][url=https://github.com/scp-fs2open/fs2open.github.com/pull/3564]added [font=Courier]Draw outlines on selected ships[/font] option in FRED[/url][/li]
[li]fixed handling arbitrary numbers of nebula poofs in FRED [url=https://github.com/scp-fs2open/fs2open.github.com/pull/3585]#3585[/url] and [url=https://github.com/scp-fs2open/fs2open.github.com/pull/3584]#3584[/url][/li]
[li]restricted briefing icon override to ships and added [font=Courier]$Custom briefing icons always override standard icons:[/font] to [font=Courier]game_settings.tbl[/font] which reverts this change [url=https://github.com/scp-fs2open/fs2open.github.com/pull/3565]#3565[/url] and [url=https://github.com/scp-fs2open/fs2open.github.com/pull/3576]#3576[/url][/li]
[li][url=https://github.com/scp-fs2open/fs2open.github.com/pull/3561]fixed subsystem debris: the engine will no longer use the specified generic debris model for destroyed subsystems since the model is usually intended to be used for destroyed ships[/url][/li]
[li][url=https://github.com/scp-fs2open/fs2open.github.com/pull/3562]support user names that contain non-ASCII characters by forcing the engine in portable mode[/url][/li]
[li][url=https://github.com/scp-fs2open/fs2open.github.com/pull/3554]add turret info to FRED's 3D view[/url][/li]
[li][url=https://github.com/scp-fs2open/fs2open.github.com/pull/3397]fixed assert when the weapon [font=Courier]None[/font] was selected as secondary weapon in FRED[/url][/li]
[li][url=https://github.com/scp-fs2open/fs2open.github.com/pull/3385]fixed variable replacement in briefings and debriefings for stages that modify variables in their conditions[/url][/li]
[li][url=https://github.com/scp-fs2open/fs2open.github.com/pull/3423]increased XSTR ID limit from 4 digits to 7 digits[/url][/li]
[li][url=https://github.com/scp-fs2open/fs2open.github.com/pull/3426]added option to disable reflect maps in the lab[/url][/li]
[li][url=https://github.com/scp-fs2open/fs2open.github.com/pull/3421]fixed the "add data" menu item in FRED's SEXP editor[/url][/li]
[li][url=https://github.com/scp-fs2open/fs2open.github.com/pull/3433]fixed crash caused by orphan weapons[/url][/li]
[li][url=https://github.com/scp-fs2open/fs2open.github.com/pull/2873]added weapon flag [font=Courier]heals[/font] which will cause the weapon to heal its target instead of dealing damage[/url][/li]
[li][url=https://github.com/scp-fs2open/fs2open.github.com/pull/3452]added [font=Courier]AmbientSnd[/font] for weapons which is emitted from the weapon itself as opposed to [font=Courier]InFlightSnd[/font] which is played as a HUD sound[/url][/li]
[li][url=https://github.com/scp-fs2open/fs2open.github.com/pull/3449]added SEXP containers[/url] [url=https://www.hard-light.net/forums/index.php?topic=88613.0]more details[/url][/li]
[li][url=https://github.com/scp-fs2open/fs2open.github.com/pull/3442]fixed culling for homing primaries (this used to break homing lasers)[/url][/li]
[li][url=https://github.com/scp-fs2open/fs2open.github.com/pull/3431]fixed AI targeting itself when hit by EMP[/url][/li]
[li][url=https://github.com/scp-fs2open/fs2open.github.com/pull/3446]added volume effect type for particle effects which spawns particles in a spherical volume (further tweaks possible through options)[/url][/li]
[li][url=https://github.com/scp-fs2open/fs2open.github.com/pull/3460]fixed [font=Courier]$Max Missiles Locked on Player:[/font] to only apply to the player[/url][/li]
[li][url=https://github.com/scp-fs2open/fs2open.github.com/pull/3437]added self-shadows for cockpits[/url][/li]
[li][url=https://github.com/scp-fs2open/fs2open.github.com/pull/3435]added [font=Courier]$Shadow Cascade Distances:[/font] to [font=Courier]game_settings.tbl[/font][/url][/li]
[li]performance improvements ([url=https://github.com/scp-fs2open/fs2open.github.com/pull/3540]properly cull debris[/url], [url=https://github.com/scp-fs2open/fs2open.github.com/pull/3535]improve matrix multiplication[/url], [url=https://github.com/scp-fs2open/fs2open.github.com/pull/3360]reduce script overhead caused by unused script hooks[/url], [url=https://github.com/scp-fs2open/fs2open.github.com/pull/3444]improve motion debris rendering[/url])[/li]
[/list]

[b]Deprecations:[/b]
[list]
[li][url=https://github.com/scp-fs2open/fs2open.github.com/pull/3472][font=Courier]script-eval[/font] has been deprecated in favor of script-eval-block[/url][/li]
[li][url=https://github.com/scp-fs2open/fs2open.github.com/pull/3370]renamed [font=Courier]hud-set-retail-gauge-active[/font] to [font=Courier]hud-set-builtin-gauge-active[/font][/url][/li]
[/list]

Deprecations are a mechanism in FSO where a certain feature or aspect of the engine has changed or is no longer supported. Since this would normally break existing mods we have the mod table feature "[tt]$Target Version:[/tt]" with which a mod can specify what version of FSO it was developed with. The features listed above will be removed or changed when the target version of a mod is at least the version released in this post.

[size=5pt]Previous [url=https://www.hard-light.net/forums/index.php?topic=97293.0]21.0 Release Thread[/url][/size]

Launchers, if you don't have one already:
[b]All platforms: [/b] For every day use, we recommend [url=https://www.hard-light.net/forums/index.php?topic=94068.0]Knossos[/url], an integrated solution for downloading and launching mods.

[hidden=Alternative Launchers]
Cross-platform: [url=http://www.hard-light.net/forums/index.php?topic=89162]wxLauncher 0.12.x Test Build[/url] (ongoing project for a unified launcher, you should upgrade to the latest RC/test build if you have not yet)
[b]Important:[/b] For best compatibility with FSO 3.8 and later you should use at least wxLauncher 0.12.

Windows:  [url=http://scp.fsmods.net/files/Launcher55g.zip]Launcher 5.5g[/url] ([url=http://scp.indiegames.us/builds/Launcher55g.zip]Mirror[/url]) ([url=http://www.mediafire.com/?wdvzn7hhhzh418m]Mirror[/url]) Not compatible with Windows 8+, use wxLauncher above
OS X:  Soulstorm's [url=http://www.hard-light.net/forums/index.php/topic,51391.0.html]OS X Launcher 3.0[/url]
Linux:  [url=http://www.hard-light.net/forums/index.php/topic,53206.0.html]YAL[/url] or [url=http://www.hard-light.net/wiki/index.php/Fs2_open_on_Linux/Graphics_Settings]by hand[/url] or whatever you can figure out.[/hidden]

[img]http://scp.indiegames.us/img/windows-icon.png[/img] [color=green][size=12pt]Windows (32/64-bit)[/size][/color]
[size=8pt]Compiled using GitHub Actions on Windows Server 2019 (10.0.17763), Visual Studio Enterprise 2019[/size]

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

[img]http://scp.indiegames.us/img/linux-icon.png[/img] [color=green][size=12pt]Linux 64-bit[/size][/color]
[size=8pt]Compiled with Ubuntu 16.04 LTS 64-bit, GCC 5[/size]
${build(groups["Linux"].mainFile)}

These builds use a mechanism called [url=http://appimage.org/]AppImage[/url] which should allow these builds to run on most Linux distributions. However, we recommend that you compile your own builds which will result in less issues.
Alternatively, if there is a package in your software repository then you should use that. If you are the maintainer of such a package for a distribution then let us know and we will include that here.


[img]http://scp.indiegames.us/img/mac-icon.png[/img] [color=green][size=12pt]OS X[/size][/color]
[b][color=red]Not available[/color][/b] We recently lost access to our Mac CI environment which we usually used for compiling these builds so for the time being, there will be no builds for this OS.

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
