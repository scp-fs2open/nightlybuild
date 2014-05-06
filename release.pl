#!/usr/bin/perl -W

# Release build script version 1.0.0
# 1.0 - Initial release

use strict;
# Switch top line to -w for production, -W for testing

use Buildcore;
use Smf;
use Git;
use Svn;
use Replacer;
use Cwd;
use Data::Dumper;
use Config::Tiny;
use Getopt::Long;
use File::Copy;
use File::Path;
use File::Spec::Functions;
use File::Basename;
use lib dirname (__FILE__);

my $CONFIG = Config::Tiny->new();
$CONFIG = Config::Tiny->read(dirname (__FILE__) . "/buildconfig.conf"); # Read in the ftp and forum authentication info
if(!(Config::Tiny->errstr() eq "")) { die "Could not read config file, did you copy the sample to buildconfig.conf and edit it?\n"; }
my $OS = Buildcore::getOS();
if(!$OS) { die "Unrecognized OS.\n"; }

my $createbranch;
my $doarchive;
my $oldreleasepost;
my $message = '';
my $vcs = ucfirst($CONFIG->{general}->{vcs})->new( 'source_path' => $CONFIG->{$OS}->{source_path}, 'OS' => $OS );
my $checkout_path = '';
my %versions = (
	'lastversion' => '',
	'lastsubversion' => '',
	'lastreleaserevision' => '',
	'nextversion' => '',
	'nextsubversion' => '',
	'nextreleaserevision' => '',
);
my $naturalversion;
my $fullversion;
my %archives;
my %md5s;

# The map of files to do replacements in, and what functions to run to do the replacements.
my %files = (
	"code/fred2/fred.rc|raw" => ["replace_revision_commas", "replace_revision_periods", "replace_natural_version"],
	"code/freespace2/freespace.rc|raw" => ["replace_revision_commas", "replace_revision_periods", "replace_natural_version"],
	"code/globalincs/version.h" => ["replace_version_major", "replace_version_minor", "replace_version_build", "replace_version_revision"],
	"configure.ac" => ["replace_spaces_only"],
	"projects/codeblocks/Freespace2/Freespace2.cbp" => ["replace_msvc_version"],
	"projects/MSVC_2005/Fred2.vcproj" => ["replace_msvc_version"],
	"projects/MSVC_2005/Freespace2.vcproj" => ["replace_msvc_version"],
	"projects/MSVC_2005/wxFRED2.vcproj" => ["replace_msvc_version"],
	"projects/MSVC_2008/Fred2.vcproj" => ["replace_msvc_version", "replace_msvc2008_tts"],
	"projects/MSVC_2008/Freespace2.vcproj" => ["replace_msvc_version", "replace_msvc2008_tts", "replace_msvc2008_voicer"],
	"projects/MSVC_2008/code.vcproj" => ["replace_msvc2008_tts"],
	"projects/MSVC_2010/Fred2.vcxproj" => ["replace_msvc_version"],
	"projects/MSVC_2010/Freespace2.vcxproj" => ["replace_msvc_version"],
	"projects/MSVC_2010/wxFRED2.vcxproj" => ["replace_msvc_version"],
	"projects/MSVC_2011/Fred2.vcxproj" => ["replace_msvc_version"],
	"projects/MSVC_2011/Freespace2.vcxproj" => ["replace_msvc_version"],
	"projects/MSVC_2011/wxFRED2.vcxproj" => ["replace_msvc_version"],
	"projects/MSVC_6/Fred2.dsp" => ["replace_msvc_version"],
	"projects/MSVC_6/Freespace2.dsp" => ["replace_msvc_version"],
	"projects/MSVC_6/wxFRED2.dsp" => ["replace_msvc_version"],
	"projects/Xcode/English.lproj/InfoPlist.strings|encoding(UTF-16)" => ["replace_natural_version"],
	"projects/Xcode/FS2_Open.xcodeproj/project.pbxproj" => ["replace_natural_version"],
	"projects/Xcode4/English.lproj/InfoPlist.strings|encoding(UTF-16)" => ["replace_natural_version"],
	"projects/Xcode4/FS2_Open.xcodeproj/project.pbxproj" => ["replace_natural_version"],
);

GetOptions (
	'createbranch=s' => \$createbranch,
	'lastversion=s' => \$versions{lastversion},
	'lastsubversion=s' => \$versions{lastsubversion},
	'lastreleaserevision=s' => \$versions{lastreleaserevision},
	'nextversion=s' => \$versions{nextversion},
	'nextsubversion=s' => \$versions{nextsubversion},
	'nextreleaserevision=s' => \$versions{nextreleaserevision},
	'doarchive' => \$doarchive,
	'oldreleasepost=s' => \$oldreleasepost,
	'message=s' => \$message,
);

$naturalversion = $versions{nextversion};

if($versions{nextsubversion})
{
	$naturalversion .= " " . $versions{nextsubversion};
	$fullversion = $naturalversion;
	$fullversion =~ s/\.\ /_/g;
}

Buildcore::set_version($naturalversion);

if($createbranch)
{
	print "Creating branch...\n";
	# Create a new branch in the VCS system
	$vcs->createbranch($createbranch, $versions{nextversion});
}

# Check out the branch for this version, git is just checkout in the current repo, SVN needs a new repo.
# SVN should only have this done once per release, git can't be hurt by double checking it every time.
# The VCS plugin should be able to figure out what to do here.
print "Checking out or updating to branch version...";
$checkout_path = $vcs->checkout_update($versions{nextversion});

if($versions{lastversion})
{
	# The fun part.  Replacing all the instances of the old version in the code with the new version.
	# There are only several formats for the version string, probably create a list of files to
	# apply a regex replace to for each one.
	print "Replacing versions...\n";
	Replacer::replace_versions(\%files, \%versions, $checkout_path);
	print "Committing versions...\n";
	$vcs->commit_versions($checkout_path, $versions{nextversion}, ($versions{nextsubversion} ? $versions{nextsubversion} : "Final"));
}

print "Exporting code...\n";
if($vcs->export($checkout_path, $versions{nextversion}, $versions{nextsubversion}) != 1)
{
	die "Export to " . $vcs->{exportpath} . " failed...\n";
}

if($doarchive)
{
	print "Archiving source...\n";
	archive_source();
	print "Uploading source...\n";
	Buildcore::upload("fs2_open_" . $fullversion . "_src.tgz", "fs2_open_" . $fullversion . "_src.md5", dirname($checkout_path), '');
	print "Moving source...\n";
	move_to_builds();
}

print "Compiling...\n";
if(Buildcore::compile($vcs->{exportpath}) != 1)
{
	die "Compile failed...\n";
}

%archives = Buildcore::get_archives();
%md5s = Buildcore::get_md5s();

print "Compiling completed\n";
# Code was compiled and updated, move the built files somewhere for archiving
print "Deleting code export...\n";
rmtree($vcs->{exportpath});

print "Uploading builds...\n";
foreach (keys (%archives))
{
	Buildcore::upload($archives{$_}, $md5s{$_}, $CONFIG->{$OS}->{archive_path}, $OS);
}

if($message ne '')
{
	post();
}

#############SUBROUTINES################


sub archive_source
{
	my $currentdir = cwd();

	chdir(dirname($checkout_path));
	my $cmd = "tar -cvzf fs2_open_" . $fullversion . "_src.tgz fs2_open_" . $fullversion;
	print $cmd . "\n";
	`$cmd`;
	$cmd = "md5sum fs2_open_" . $fullversion . "_src.tgz > fs2_open_" . $fullversion . "_src.md5";
	print $cmd . "\n";
	`$cmd`;
	chdir($currentdir);
}

sub move_to_builds
{
	my $currentdir = cwd();

	chdir(dirname($checkout_path));
	move("fs2_open_" . $fullversion . "_src.tgz", catfile("builds", "fs2_open_" . $fullversion . "_src.tgz"));
	move("fs2_open_" . $fullversion . "_src.md5", catfile("builds", "fs2_open_" . $fullversion . "_src.md5"));
	chdir($currentdir);
}

sub post
{
	my $subject;
	my $logoutput;
	my $archivename;
	my $md5name;
	my $underscoreversion = $naturalversion;
	$underscoreversion =~ s/\.\ /_/g;
	my $periodversion = $naturalversion;
	$periodversion =~ s/\ /_/g;

	print "In the post function, submitting post to builds area...\n";

	# Set up the Subject
	$subject = "Release: " . $versions{nextversion} . ' ' . ($versions{nextsubversion} ? $versions{nextsubversion} : "Final");
	# Set up the message
	$message .= "\n\n[size=12pt]Important!![/size]
As always, you need OpenAL installed.  Linux and OS X come with it but Windows users will need to get Creative's [url=http://scp.indiegames.us/builds/oalinst.zip]OpenAL installer[/url].

[size=12pt]Important!![/size]
Also, since the internal code linking for TrackIR was revised, an external DLL is now required for FSO to use TrackIR functions.
The following DLL is simply unpacked in to you main FreeSpace2 root dir.
TrackIR is only supported on Windows.
[url=http://www.mediafire.com/download.php?ihzkihqj2ky]TrackIR SCP DLL[/url] ([url=http://swc.fs2downloads.com/builds/scptrackir.zip]Mirror[/url]) ([url=http://scp.fsmods.net/builds/scptrackir.zip]Mirror[/url]) ([url=http://scp.indiegames.us/builds/scptrackir.zip]Mirror[/url])

Launchers, if you don't have one already:
All platforms:  [url=http://www.hard-light.net/forums/index.php?topic=67950.0]wxLauncher[/url] (ongoing project for a unified launcher)
-or-
Windows:  [url=http://swc.fs2downloads.com/files/Launcher55g.zip]Launcher 5.5g[/url] ([url=http://scp.fsmods.net/builds/Launcher55g.zip]Mirror[/url]) ([url=http://scp.indiegames.us/builds/Launcher55g.zip]Mirror[/url]) ([url=http://www.mediafire.com/?wdvzn7hhhzh418m]Mirror[/url]) Not compatible with Windows 8, use wxLauncher above
OS X:  Soulstorm's [url=http://www.hard-light.net/forums/index.php/topic,51391.0.html]OS X Launcher 3.0[/url]
Linux:  [url=http://www.hard-light.net/forums/index.php/topic,53206.0.html]YAL[/url] or [url=http://www.hard-light.net/wiki/index.php/Fs2_open_on_Linux/Graphics_Settings]by hand[/url] or whatever you can figure out.

Known issues:
[list]
[li]See the list of [url=http://scp.indiegames.us/mantis/search.php?project_id=1&status_id%5B%5D=10&status_id%5B%5D=20&status_id%5B%5D=30&status_id%5B%5D=40&status_id%5B%5D=50&priority_id%5B%5D=40&priority_id%5B%5D=50&priority_id%5B%5D=60&sticky_issues=on&sortby=last_updated&dir=DESC&per_page=200&hide_status_id=-2]Fix for next release[/url] bugs - mark a bug as an elevated priority (high, urgent, immediate) to get it included in that filter.[/li]
[li]Here is the filter for [url=http://scp.indiegames.us/mantis/search.php?project_id=1&status_id%5B%5D=10&status_id%5B%5D=20&status_id%5B%5D=30&status_id%5B%5D=40&status_id%5B%5D=50&status_id%5B%5D=60&sticky_issues=on&target_version=" . $versions{nextversion} . "&sortby=last_updated&dir=DESC&hide_status_id=-2]Target " . $versions{nextversion} . "[/url] bugs.[/li]
[/list]


[img]http://scp.indiegames.us/img/windows-icon.png[/img] [color=green][size=12pt]Windows[/size][/color] ([color=yellow][url=http://swc.fs2downloads.com/builds/WIN/fs2_open_" . $underscoreversion . ".md5]MD5s[/url][/color])
Compiled on MSVC 2008 SP1

[b]If you don't know which one to get, get the third one (no SSE).[/b]  [color=red]If you don't know what SSE means, read this: http://en.wikipedia.org/wiki/Streaming_SIMD_Extensions[/color]
You can use freely available tools like [url=http://www.cpuid.com/softwares/cpu-z.html]CPU-Z[/url] to check which SSE capabilities your CPU has.

[url=http://swc.fs2downloads.com/builds/WIN/fs2_open_" . $underscoreversion . ".zip]fs2_open_" . $underscoreversion . ".zip[/url] ([url=http://scp.fsmods.net/builds/WIN/fs2_open_" . $underscoreversion . ".zip]Mirror[/url]) ([url=http://scp.indiegames.us/builds/WIN/fs2_open_" . $underscoreversion . ".zip]Mirror[/url])
This one is based on the SSE2 Optimizations from the MSVC Compiler.

[url=http://swc.fs2downloads.com/builds/WIN/fs2_open_" . $underscoreversion . "_SSE.zip]fs2_open_" . $underscoreversion . "_SSE.zip[/url] ([url=http://scp.fsmods.net/builds/WIN/fs2_open_" . $underscoreversion . "_SSE.zip]Mirror[/url]) ([url=http://scp.indiegames.us/builds/WIN/fs2_open_" . $underscoreversion . "_SSE.zip]Mirror[/url])
This one is based on the SSE Optimizations from the MSVC Compiler.

[url=http://swc.fs2downloads.com/builds/WIN/fs2_open_" . $underscoreversion . "_NO-SSE.zip]fs2_open_" . $underscoreversion . "_NO-SSE.zip[/url] ([url=http://scp.fsmods.net/builds/WIN/fs2_open_" . $underscoreversion . "_NO-SSE.zip]Mirror[/url]) ([url=http://scp.indiegames.us/builds/WIN/fs2_open_" . $underscoreversion . "_NO-SSE.zip]Mirror[/url])

[url=http://scp.indiegames.us/builds/WIN/fs2_open_" . $underscoreversion . "_WIN9X.zip]fs2_open_" . $underscoreversion . "_WIN9X.zip[/url]
For Windows 98, Windows ME, and Windows 2000.

[b]What are those SSE and SSE2 builds I keep seeing everywhere?[/b]
[url=http://www.hard-light.net/forums/index.php?topic=65628.0]Your answer is in this topic.[/url]


[img]http://scp.indiegames.us/img/mac-icon.png[/img] [color=green][size=12pt]OS X Universal (32/64-bit Intel)[/size][/color] ([color=yellow][url=http://swc.fs2downloads.com/builds/OSX/FS2_Open-" . $periodversion . ".md5]MD5s[/url][/color])
Compiled on Xcode 5.1.1

[url=http://swc.fs2downloads.com/builds/OSX/FS2_Open-" . $periodversion . ".dmg]FS2_Open-" . $periodversion . ".dmg[/url] ([url=http://scp.fsmods.net/builds/OSX/FS2_Open-" . $periodversion . ".dmg]Mirror[/url]) ([url=http://scp.indiegames.us/builds/OSX/FS2_Open-" . $periodversion . ".dmg]Mirror[/url])


[img]http://scp.indiegames.us/img/linux-icon.png[/img] [color=green][size=12pt]Linux 32-bit[/size][/color] ([color=yellow][url=http://swc.fs2downloads.com/builds/LINUX/fs2_open_" . $periodversion . ".md5]MD5s[/url][/color])
Compiled on Ubuntu 12.04 LTS 32bit, GCC 4.6.3

[url=http://swc.fs2downloads.com/builds/LINUX/fs2_open_" . $periodversion . ".tar.bz2]fs2_open_" . $periodversion . ".tar.bz2[/url] ([url=http://scp.fsmods.net/builds/LINUX/fs2_open_" . $periodversion . ".tar.bz2]Mirror[/url]) ([url=http://scp.indiegames.us/builds/LINUX/fs2_open_" . $periodversion . ".tar.bz2]Mirror[/url])


[img]http://scp.indiegames.us/img/freebsd-icon.png[/img] [color=green][size=12pt]FreeBSD 64-bit (experimental, limited support)[/size][/color] ([color=yellow][url=http://swc.fs2downloads.com/builds/FREEBSD/fs2_open_" . $periodversion . ".md5]MD5s[/url][/color])
Compiled on GhostBSD LXDE 3.0 64-bit, GCC 4.2.1

[url=http://swc.fs2downloads.com/builds/FREEBSD/fs2_open_" . $periodversion . ".tar.bz2]fs2_open_" . $periodversion . ".tar.bz2[/url] ([url=http://scp.fsmods.net/builds/FREEBSD/fs2_open_" . $periodversion . ".tar.bz2]Mirror[/url]) ([url=http://scp.indiegames.us/builds/FREEBSD/fs2_open_" . $periodversion . ".tar.bz2]Mirror[/url])

[color=green][size=12pt]Source Code Export[/size][/color] ([color=yellow][url=http://swc.fs2downloads.com/builds/fs2_open_" . $underscoreversion . "_src.md5]MD5[/url][/color])
[url=http://swc.fs2downloads.com/builds/fs2_open_" . $underscoreversion . "_src.tgz]fs2_open_" . $underscoreversion . "_src.tgz[/url] ([url=http://scp.fsmods.net/builds/fs2_open_" . $underscoreversion . "_src.tgz]Mirror[/url]) ([url=http://scp.indiegames.us/builds/fs2_open_" . $underscoreversion . "_src.tgz]Mirror[/url])";

	Smf::set_homeurl($CONFIG->{general}->{forum_url});
	Smf::set_board($CONFIG->{$OS}->{release_forum});
	Smf::set_username($CONFIG->{forum}->{username});
	Smf::set_password($CONFIG->{forum}->{password});
	Smf::set_smfversion($CONFIG->{forum}->{smfversion});
	Smf::post($subject, $message);
}
