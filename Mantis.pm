package Mantis;

# MantisConnect API using SOAP::Lite 1.0.0
# 1.0 Initial Release

use strict;
use warnings;

use Data::Dumper;
use SOAP::Lite
	uri => 'http://futureware.biz/mantisconnect';

my $proxy;
my $uri;

sub new
{
	my $type = shift;
	my %parm = @_;
	my $this = {};  # Create an anonymous hash, and #self points to it.

	$this->{connecturl} = $parm{connecturl};
	$this->{proxy} = $parm{proxy};
	$this->{username} = $parm{username};
	$this->{password} = $parm{password};
	$this->{projectid} = $parm{projectid};
	$this->{soap} = SOAP::Lite
	-> proxy($this->{connecturl}, proxy => ['http' => $this->{proxy}]);

	bless $this, $type;       # Connect the hash to the package Mantis.
	return $this;     # Return the reference to the hash.
}

# Gets the issues count for a given filter ID.
sub get_issues_count
{
	my ($class, $filterid) = @_;

	my @issues = $class->{soap}
	-> mc_filter_get_issue_headers($class->{username}, $class->{password}, $class->{projectid}, $filterid, 1, -1)
	-> result;

	return 0+@{ $issues[0] };
}

return 1;
