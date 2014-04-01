package Svn;

# SVN Nightlybuild Plugin 1.0
# 1.0 - Initial release

use strict;
use warnings;

require Vcs;
use base 'Vcs';

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
		print "Unrecognized data:\n" . $updateoutput . "\n";
		$class->{revision} = "FAILURE";
		return 0;
	}
}

sub export
{
	my ($class) = @_;
	my $exportoutput;
	my $exportcommand;
	my $i = 0;

	do {
		$class->{exportpath} = $class->{source_path} . "_" . $i++;
	} while (-d $class->{exportpath});

	print "Going to export " . $class->{source_path} . " to directory " . $class->{exportpath} . "\n";

	$exportcommand = "svn export " . $class->{source_path} . " " . $class->{exportpath};
#	print $exportcommand . "\n";
	$exportoutput = `$exportcommand`;

	if($exportoutput =~ /Export\ complete.\s*$/)
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
