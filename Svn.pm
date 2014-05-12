package Svn;

# SVN Nightlybuild Plugin 2.0
# 2.0 - Support for release building as well as nightly building
# 1.0 - Initial release

use strict;
use warnings;

use File::Basename;
use lib dirname (__FILE__);
use File::Spec::Functions;
use Config::Tiny;
require Vcs;
use base 'Vcs';

my $CONFIG = Config::Tiny->new();
$CONFIG = Config::Tiny->read(dirname (__FILE__) . "/Svn.conf"); # Read in the plugin config info
if(!(Config::Tiny->errstr() eq "")) { die "Could not read config file, did you copy the sample to Svn.conf and edit it?\n"; }

sub new
{
	my $type = shift;
	my %parm = @_;
	my $this = Vcs->new(%parm);  # Create an anonymous hash, and #self points to it.

	bless $this, $type;       # Connect the hash to the package SVN.
	return $this;     # Return the reference to the hash.
}

sub getrevision
{
	my ($class) = @_;
	my $command;
	$command = "svnversion -n " . $class->{source_path};
	return `$command 2>&1`;
}

sub createbranch
{
	my ($class, $revision, $version) = @_;
	my $dirversion;
	my $cmd;

	$cmd = "svn copy -r " . $revision . " " . $CONFIG->{general}->{trunk_url} . " " . $CONFIG->{general}->{branches_url} . Vcs::get_dirbranch($version, $CONFIG->{general}->{branch_format}) . " -m 'Copy trunk r" . $revision . " to " . $version . " branch.'";
	print $cmd . "\n";
	`$cmd`;
}

sub checkout_update
{
	# Checkout the branch if not already checked out here.
	my ($class, $version) = @_;
	my $checkout_path = catfile(dirname($class->{source_path}), Vcs::get_dirbranch($version, $CONFIG->{general}->{branch_format}) . "_svn");
	my $cmd;

	unless ( -d ( $checkout_path ) )
	{
		$cmd = "svn checkout " . $CONFIG->{general}->{branches_url} . Vcs::get_dirbranch($version, $CONFIG->{general}->{branch_format}) . " " . $checkout_path;
	}
	else
	{
		$cmd = "svn up " . $checkout_path;
	}
	print $cmd . "\n";
	`$cmd`;

	return $checkout_path;
}

sub commit_versions
{
	my ($class, $checkout_path, $version, $subversion) = @_;
	my $cmd;

	$cmd = "svn commit -m 'Automated " . $version . " " . $subversion . " versioning commit' " . $checkout_path;
	print $cmd . "\n";
	`$cmd`;
}

sub update
{
	my ($class) = @_;
	my $rline = '';
	my $updateoutput;
	my $updatecommand;

	if($class->{stoprevision})
	{
		$rline = '-r ' . $class->{stoprevision} . ' ';
	}
	$updatecommand = "svn update " . $rline . $class->{source_path};

	$updateoutput = `$updatecommand`;
#	$updateoutput = "Updated to revision 4823.";

	# print $updateoutput;

	# TODO:  Simple test for now.  Later, if not At revision, filter out project file updates that don't apply and other unimportant changes.
	if($updateoutput =~ /At\ revision\ /)
	{
		# No change to source
		$updateoutput =~ /At\ revision\ (\d*)\./;
		$class->{revision} = $1;
		return 0;
	}
	elsif($updateoutput =~ /Updated\ to\ revision\ /)
	{
		# Source has changed
		$updateoutput =~ /Updated\ to\ revision\ (\d*)\./;
		$class->{revision} = $1;
		$class->{displayrevision} = $class->{revision};
		$class->{buildrevision} = 'r' . $class->{revision};
		return 1;
	}
	else
	{
		# Unexpected data received
		print STDERR "Unrecognized data:\n" . $updateoutput . "\n";
		$class->{revision} = "FAILURE";
		return 0;
	}
}

sub export
{
	my $class = shift;
	my $source;
	my $exportoutput;
	my $exportcommand;
	unless ($source = shift)
	{
		my $i = 0;
		$source = $class->{source_path};
		do {
			$class->{exportpath} = $class->{source_path} . "_" . $i++;
		} while (-d $class->{exportpath});
	}
	else
	{
		my $version = shift;
		$class->{exportpath} = catfile(dirname($source), Vcs::get_dirbranch($version, $CONFIG->{general}->{branch_format}));
		if(my $subversion = shift)
		{
			$class->{exportpath} .= "_" . $subversion;
		}
	}

	print "Going to export " . $source . " to directory " . $class->{exportpath} . "\n";

	$exportcommand = "svn export " . $source . " " . $class->{exportpath};
	print $exportcommand . "\n";
	$exportoutput = `$exportcommand`;

	if($exportoutput =~ /Export\ complete\.\s*$/)
	{
		return 1;
	}
	else
	{
		return 0;
	}
}

sub get_log
{
	my ($class) = @_;
	my $logcommand = "svn log -v -r " . ($class->{oldrevision} + 1) . ":" . $class->{revision} . " " . $class->{source_path};
	return `$logcommand`;
}

# SVN has no post-compilation cleanup to do.
sub finalize {}

1;
