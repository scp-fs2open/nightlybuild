package Git;

# Git Nightlybuild Plugin 1.0
# 1.0 - Initial release

use strict;
use warnings;

use Config::Tiny;
require Vcs;
use base 'Vcs';

my $CONFIG = Config::Tiny->new();
$CONFIG = Config::Tiny->read("Git.conf"); # Read in the plugin config info
if(!(Config::Tiny->errstr() eq "")) { die "Could not read config file, did you copy the sample to Git.conf and edit it?\n"; }

sub new
{
	my $type = shift;
	my %parm = @_;
	my $this = Vcs->new(%parm);  # Create an anonymous hash, and #self points to it.

	$this->{gitremotecmd} = "git --git-dir=" . $this->{source_path} . "/.git --work-tree=" . $this->{source_path};
	$this->{nightly_branch} = $CONFIG->{general}->{nightly_branch};
	$this->{nightly_branch} =~ s/##BRANCH##/$CONFIG->{general}->{track_branch}/;
	$this->{nightly_branch} =~ s/##OS##/$this->{'OS'}/;

	bless $this, $type;       # Connect the hash to the package Git.
	return $this;     # Return the reference to the hash.
}

sub getrevision
{
	my ($class) = @_;
	my $createcommand;
	my $command;
	my $output;
	my $fetchcommand = $class->{gitremotecmd} . " fetch";
	`$fetchcommand`;
	# See if nightly_branch exists
	system($class->{gitremotecmd} . " show-ref --verify --quiet refs/heads/" . $class->{nightly_branch});
	if($? >> 8 != 0)
	{
		# Branch does not exist yet.  Create a new one based on the remote branch,
		# or on origin/master~ if it doesn't exist yet.
		$createcommand = $class->{gitremotecmd} . " update-ref refs/heads/" . $class->{nightly_branch} . " origin/";
		system($class->{gitremotecmd} . " show-ref --verify --quiet refs/remotes/origin/" . $class->{nightly_branch});
		if($? >> 8 != 0)
		{
			# Remote branch is non-existent too.
			$createcommand = $createcommand . $CONFIG->{general}->{track_branch} . "~";
		}
		else
		{
			$createcommand = $createcommand . $class->{nightly_branch};
		}
		`$createcommand 2>&1`;
	}
	$command = $class->{gitremotecmd} . " rev-parse " . $class->{nightly_branch};
	$output = `$command 2>&1`;
	$output =~ s/^\s+|\s+$//g;

	return $output;
}

sub update
{
	my ($class) = @_;
	my $command;

	if($class->{stoprevision})
	{
		die "Git does not understand -r yet.\n";
	}

	#Compare track_branch hash to nightly_branch hash
	$command = $class->{gitremotecmd} . " rev-parse origin/" . $CONFIG->{general}->{track_branch};
	$class->{revision} = `$command 2>&1`;
	$class->{revision} =~ s/^\s+|\s+$//g;
	if($class->{revision} eq $class->{oldrevision})
	{
		# Nightly is up to date.
		return 0;
	}
	else
	{
		# Update the local branch hash to the track branch hash.
		$class->{buildrevision} = substr($class->{revision}, 0, 7);
		$class->{displayrevision} = $class->{buildrevision};
		$command = $class->{gitremotecmd} . " update-ref refs/heads/" . $class->{nightly_branch} . " " . $class->{revision};
		`$command 2>&1`;
	}

	return 1;
}

sub export
{
	my ($class) = @_;
	my $exportcommand;
	my $i = 0;

	do {
		$class->{exportpath} = $class->{source_path} . "_" . $i++;
	} while (-d $class->{exportpath});

	print "Going to export " . $class->{source_path} . " to directory " . $class->{exportpath} . "\n";

	mkdir($class->{exportpath});

	$exportcommand = $class->{gitremotecmd} . " archive --format=tar " . $class->{nightly_branch} . " | tar -C " . $class->{exportpath} . " -xf -";
	system($exportcommand);
	if($? >> 8 == 0)
	{
		# Export command returned success (0).
		return 1;
	}
	else
	{
		# Export command returned non-zero return value.
		return 0;
	}
}

sub get_log
{
	my ($class) = @_;
	my $logcommand = $class->{gitremotecmd} . " log " . $class->{revision} . " ^" . $class->{oldrevision} . " --no-merges";
	if($CONFIG->{general}->{log_pretty})
	{
		$logcommand = $logcommand . " --stat --pretty=" . $CONFIG->{general}->{log_pretty};
	}
	return `$logcommand`;
}

sub finalize
{
	my ($class) = @_;
	# Git needs to update the remote branch and push it up.
	my $command = $class->{gitremotecmd} . " push origin " . $class->{nightly_branch};
	`$command 2>&1`;
	$command = $class->{gitremotecmd} . " branch --set-upstream " . $class->{nightly_branch} . " origin/" . $class->{nightly_branch};
	`$command 2>&1`;
}

1;
