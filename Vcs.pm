package Vcs;

# Vcs Nightlybuild Plugin 1.0 - abstract class for VCS plugins to extend
# 1.0 - Initial release

use strict;
use warnings;

sub new
{
	my $type = shift;
	my %parm = @_;
	my $this = {};  # Create an anonymous hash, and #self points to it.

	$this->{source_path} = $parm{source_path};
	$this->{OS} = $parm{OS};
	$this->{stoprevision} = '';
	$this->{oldrevision} = '';
	$this->{revision} = 'FAILURE';
	$this->{buildrevision} = '';
	$this->{displayrevision} = '';
	$this->{exportpath} = '';

	bless $this, $type;       # Connect the hash to the package Vcs.
	return $this;     # Return the reference to the hash.
}

sub verifyrepo
{
	my ($class) = @_;
	unless(-d $class->{source_path})
	{
		print "Could not find source code at " . $class->{source_path} . "\n";
		$class->{revision} = "FAILURE";
		return 0;
	}
	$class->{oldrevision} = $class->getrevision();
	unless($class->{oldrevision} =~ /^[a-zA-Z0-9]+$/)
	{
		$class->{revision} = "FAILURE";
		return 0;
	}

	return 1;
}

1;
