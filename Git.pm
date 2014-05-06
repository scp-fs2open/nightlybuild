package Git;

# Git Nightlybuild Plugin 2.0
# 2.0 - Support for release building as well as nightly building
# 1.0 - Initial release

use strict;
use warnings;

use Config::Tiny;
use File::Spec::Functions;
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

	$this->{gitremotecmd} = "git --git-dir=" . catfile($this->{source_path}, ".git") . " --work-tree=" . $this->{source_path};
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

sub createbranch
{
	my ($class, $revision, $version) = @_;
	my $cmd = $class->{gitremotecmd} . " update-ref refs/heads/" . Vcs::get_dirbranch($version, $CONFIG->{general}->{branch_format}) . " " . $revision;
	print $cmd . "\n";
	`$cmd`;
	$cmd = $class->{gitremotecmd} . " push origin " . Vcs::get_dirbranch($version, $CONFIG->{general}->{branch_format});
	print $cmd . "\n";
	`$cmd`;
}

sub checkout_update
{
	my ($class, $version) = @_;
	my $cmd = $class->{gitremotecmd} . " checkout " . Vcs::get_dirbranch($version, $CONFIG->{general}->{branch_format});
	print $cmd . "\n";
	`$cmd`;
	$cmd = $class->{gitremotecmd} . " pull";
	print $cmd . "\n";
	`$cmd`;

	return $class->{source_path};
}

sub commit_versions
{
	my ($class, $checkout_path, $version, $subversion) = @_;
	my $cmd;

	$cmd = $class->{gitremotecmd} . " commit -am 'Automated " . $version . " " . $subversion . " versioning commit'";
	print $cmd . "\n";
	`$cmd`;
	$cmd = $class->{gitremotecmd} . " push origin " . Vcs::get_dirbranch($version, $CONFIG->{general}->{branch_format});
	print $cmd . "\n";
	`$cmd`;
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
	my $class = shift;
	my $source;
	my $exportcommand;
	unless($source = shift)
	{
		my $i = 0;
		$source = $class->{source_path};

		do {
			$class->{exportpath} = $source . "_" . $i++;
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
