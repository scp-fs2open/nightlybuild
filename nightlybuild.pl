#!/usr/bin/perl -W

# Nightly build script version 3.3.0
# 3.3.0 - Add support for replacing the FS_VERSION_IDENT in nightlies
# 3.2.0 - Use new Mantis module to get number of currently open issues
# 3.1.0 - Use Buildcore's new SHA-256 support
# 3.0.0 - Remaining shared functionality with release script moved into common Buildcore plugin
# 2.0.0 - Git support!  Moved VCS-related functions into plugins, including a parent plugin for all VCS modules.
# 1.7.3 - Forgot to update default MSVC2008 build name pattern matching when the names changed a while back.
# 1.7.2 - Fixed OS X not renaming .dSYMs properly, change default OS X project to Xcode4, escaping whitespace in regex, deleting temp build files on OS X, better old revision checking
# 1.7.1 - Fixed another bug with subversion regex
# 1.7.0 - Changed config file default name in SVN, so make sure it was copied to buildconfig.conf before continuing.
# 1.6.9 - FreeBSD support
# 1.6.3 - Fix an export bug
# 1.6.2 - Fix a problem with stoprevision not working.
# 1.6.1 - Ability to use the SMF package's version setting
# 1.6.0 - Added stoprevision command line support, shifted around some debug output
# 1.5.1 - Fix problems with VS2008, to allow spaces in config names.
# 1.5.0 - Big update to allow for building more configs and grouping them into different archives, all in the same post.
# 1.4.4 - Grab the VC2008 pdb files by changing the regex in the config
# 1.4.3 - fix a move issue, use the config name for the folder and not the config string
# 1.4.2 - fix some more issues with the export method
# 1.4.1 - just a bit more cleanup
# 1.4 - performs a local export before compiling for clean working dir, also checks Linux build output for error
# 1.3.1 - checks for most directories instead of assuming they exist
# 1.3 - cleans builds every compile, supports VC6 as well as VC2008, set up options in config file
# 1.2 - added a lot of error checking, mostly making sure files exist at every step, does some output parsing for error statements
# 1.1 - support for Linux (make) and OS X (xcodebuild), switched to ini style config
# 1.0 - Support for Windows via MSVC2008

use strict;
# Switch top line to -w for production, -W for testing

use File::Basename;
use lib dirname (__FILE__);
use Buildcore;
use Smf;
use Git;
use Svn;
use Replacer;
use Mantis;
use Data::Dumper;
use Config::Tiny;
use Getopt::Long;
use File::Path;

my $CONFIG = Config::Tiny->new();
$CONFIG = Config::Tiny->read(dirname (__FILE__) . "/buildconfig.conf"); # Read in the ftp and forum authentication info
if(!(Config::Tiny->errstr() eq "")) { die "Could not read config file, did you copy the sample to buildconfig.conf and edit it?\n"; }
my $OS = Buildcore::getOS();
if(!$OS) { die "Unrecognized OS.\n"; }

my ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime;
my @months = qw(01 02 03 04 05 06 07 08 09 10 11 12);
my @abbr = qw( Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec );
$year += 1900;
my $monthword = $abbr[$mon];
$mon = $months[$mon];
if($mday < 10)
{
	$mday = "0" . $mday;
}
my $DATE = $year . $mon . $mday;

my %archives;
my %dmgs;
my %md5s;
my %shas;

my $vcs = ucfirst($CONFIG->{general}->{vcs})->new( 'source_path' => $CONFIG->{$OS}->{source_path}, 'OS' => $OS );

my %files = (
	"code/fred2/fred.rc|raw" => ["inject_revision"],
	"code/freespace2/freespace.rc|raw" => ["inject_revision"],
	"code/globalincs/version.h" => ["inject_revision", "inject_ident"],
);

my %versions = (
	'lastreleaserevision' => '000000',
	'nextreleaserevision' => '',
	'lastident' => 'custom',
	'nextident' => '',
);

my $mantis = Mantis->new(
	connecturl => $CONFIG->{mantis}->{installation_base_url} . 'api/soap/mantisconnect.php',
	username => $CONFIG->{mantis}->{username},
	password => $CONFIG->{mantis}->{password},
	projectid => $CONFIG->{mantis}->{projectid}
);

my $open_issues = $mantis->get_issues_count($CONFIG->{mantis}->{open_issues_filter_id});

GetOptions ('stoprevision=s' => \$vcs->{stoprevision});

if(!$vcs->verifyrepo() || $vcs->update() != 1)
{
	if($vcs->{revision} eq "FAILURE")
	{
		die "Error checking for a revision change, terminating.\n";
	}
	else
	{
		print "Repository still at revision " . $vcs->{revision} . ", terminating.\n";
		exit;
	}
}

print "Repository has been updated to revision " . $vcs->{revision} . ", compiling...\n";

$versions{nextreleaserevision} = $vcs->{fsrevision};
$versions{nextident} = $vcs->{ident};
Buildcore::set_basename_suffix("_" . $DATE . "_" . $vcs->{buildrevision});

if($vcs->export() != 1)
{
	die "Export to " . $vcs->{exportpath} . " failed...\n";
}

Replacer::replace_versions(\%files, \%versions, $vcs->{exportpath});

# call Compile scripts
if(Buildcore::compile($vcs->{exportpath}) != 1)
{
	die "Compile failed...\n";
}

%archives = Buildcore::get_archives();
%dmgs = Buildcore::get_dmgs();
%md5s = Buildcore::get_md5s();
%shas = Buildcore::get_shas();

print "Compiling completed\n";
# Code was compiled and updated, move the built files somewhere for archiving
rmtree($vcs->{exportpath});

foreach (keys (%archives))
{
	Buildcore::upload($archives{$_}, $dmgs{$_}, $md5s{$_}, $shas{$_}, $CONFIG->{$OS}->{archive_path}, $OS);
}

post();

$vcs->finalize();

#############SUBROUTINES################


sub post
{
	my $subject;
	my $message;
	my $logoutput;
	my $archivename;
	my $md5name;
	my $group;
	my $mirror;
	my %MIRROR_DOWNLOAD_PATHS;
	my @mirrors = split(/~/, $CONFIG->{general}->{Buildcore::get_mode() . '_mirrors'});
	@MIRROR_DOWNLOAD_PATHS{split(/~/, $CONFIG->{mirrors}->{names})} = split(/::/, $CONFIG->{mirrors}->{download_paths});
	my $n = 1;

	print "In the post function, submitting post to builds area...\n";

	$logoutput = $vcs->get_log();

	# Set up the Subject
	$subject = "Nightly (" . $CONFIG->{$OS}->{os_name} . "): " . $mday . " " . $monthword . " " . $year . " - Revision " . $vcs->{displayrevision};
	# Set up the message
	$message = "Here is the nightly for " . $CONFIG->{$OS}->{os_name} . " on " . $mday . " " . $monthword . " " . $year . " - Revision " . $vcs->{displayrevision} . "\n\n";
	$message .= "Open non-feature issues in [url=" . $CONFIG->{mantis}->{installation_base_url} . "view_all_set.php?type=3&source_query_id=" . $CONFIG->{mantis}->{open_issues_filter_id} . "]Mantis[/url]: " . $open_issues . "\n\n";

	# Make a post on the forums to the download
	foreach $group (keys (%archives))
	{
		$archivename = $archives{$group};
		$md5name = $md5s{$group};
		$message .= "Group: " . $group . "\n";
		foreach $mirror (@mirrors)
		{
			$message .= "[url=".$MIRROR_DOWNLOAD_PATHS{$mirror}.$OS."/".$archivename."]".$archivename."[/url]\n";
			$message .= "[url=".$MIRROR_DOWNLOAD_PATHS{$mirror}.$OS."/".$md5name."]MD5Sum[/url]\n";
			if( (0 + @mirrors) > $n++ )
			{
				$message .= "Mirror " . $n . "\n";
			}
		}
		$message .= "\n";
	}

	$message .= "[code]\n";
	$message .= $logoutput . "\n";
	$message .= "[/code]\n\n";

	Smf::set_homeurl($CONFIG->{general}->{forum_url});
	Smf::set_board($CONFIG->{$OS}->{builds_forum});
	Smf::set_username($CONFIG->{forum}->{username});
	Smf::set_password($CONFIG->{forum}->{password});
	Smf::set_smfversion($CONFIG->{forum}->{smfversion});
	Smf::post($subject, $message);
}
