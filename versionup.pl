#!/usr/bin/perl -W

# Version bump script 1.0.0
# 1.0.0 - Initial release

use strict;
use warnings;

use Buildcore;
use Git;
use Svn;
use Replacer;
use Getopt::Long;
use Config::Tiny;
use File::Basename;
use lib dirname (__FILE__);

my $CONFIG = Config::Tiny->new();
$CONFIG = Config::Tiny->read(dirname (__FILE__) . "/buildconfig.conf"); # Read in the ftp and forum authentication info
if(!(Config::Tiny->errstr() eq "")) { die "Could not read config file, did you copy the sample to buildconfig.conf and edit it?\n"; }
my $OS = Buildcore::getOS();
if(!$OS) { die "Unrecognized OS.\n"; }

my %versions = (
	'lastversion' => '',
	'lastsubversion' => '',
	'lastreleaserevision' => '000000',
	'nextversion' => '',
	'nextsubversion' => '',
	'nextreleaserevision' => '000000',
);

# The map of files to do replacements in, and what functions to run to do the replacements.
my %files = (
	"code/fred2/fred.rc|raw" => ["replace_revision_commas", "replace_revision_periods", "replace_natural_version"],
	"code/freespace2/freespace.rc|raw" => ["replace_revision_commas", "replace_revision_periods", "replace_natural_version"],
	"code/globalincs/version.h" => ["replace_version_major", "replace_version_minor", "replace_version_build", "replace_version_revision"],
	"configure.ac" => ["replace_spaces_only"],
	"projects/codeblocks/Freespace2/Freespace2.cbp" => ["replace_msvc_version"],
	"projects/MSVC_2010/Fred2.vcxproj" => ["replace_msvc_version"],
	"projects/MSVC_2010/Freespace2.vcxproj" => ["replace_msvc_version"],
	"projects/MSVC_2010/wxFRED2.vcxproj" => ["replace_msvc_version"],
	"projects/MSVC_2013/Fred2.vcxproj" => ["replace_msvc_version"],
	"projects/MSVC_2013/Freespace2.vcxproj" => ["replace_msvc_version"],
	"projects/MSVC_2013/wxFRED2.vcxproj" => ["replace_msvc_version"],
	"projects/MSVC_2015/Fred2.vcxproj" => ["replace_msvc_version"],
	"projects/MSVC_2015/Freespace2.vcxproj" => ["replace_msvc_version"],
	"projects/MSVC_2015/wxFRED2.vcxproj" => ["replace_msvc_version"],
	"projects/Xcode/English.lproj/InfoPlist.strings|encoding(UTF-16)" => ["replace_natural_version"],
	"projects/Xcode/FS2_Open.xcodeproj/project.pbxproj" => ["replace_natural_version"],
);

my $vcs = ucfirst($CONFIG->{general}->{vcs})->new( 'source_path' => $CONFIG->{$OS}->{source_path}, 'OS' => $OS );

GetOptions (
	'lastversion=s' => \$versions{lastversion},
	'nextversion=s' => \$versions{nextversion},
);

if($versions{lastversion})
{
	# The fun part.  Replacing all the instances of the old version in the code with the new version.
	# There are only several formats for the version string, probably create a list of files to
	# apply a regex replace to for each one.
	print "Replacing versions...\n";
	Replacer::replace_versions(\%files, \%versions, $vcs->{source_path});
	print "Committing versions...\n";
	$vcs->commit_versions($vcs->{source_path}, $versions{nextversion}, "");
}
