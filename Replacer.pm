package Replacer;

# Replacer Nightlybuild Plugin 1.0
# 1.0 - Initial release

use strict;
use warnings;

use Data::Dumper;
use File::Spec::Functions;

my $raw_regex;

sub replace_versions
{
	my $files_ref = shift;
	my $versions_ref = shift;
	my $path = shift;
	my %files = %$files_ref;
	my @value;
	my $file;
	my $functions;
	for $file ( keys %files )
	{
		@value = @{$files{$file}};
		while ($functions = shift(@value))
		{
			Replacer::replace($file, $path, $versions_ref, $functions);
		}
	}
}

sub replace
{
	my ($filename, $checkout_path, $versions_ref, @functions) = @_;
	my $function;
	my $encoding = "encoding(UTF-8)";
	if($filename =~ /\|/)
	{
		($filename, $encoding) = split(/\|/, $filename);
	}

	while ($function = shift(@functions))
	{
		$raw_regex = 0;
		$function = "Replacer::" . $function;
		my ($search, $replace) = &{\&{$function}}($versions_ref);
		replace_in_file( catfile($checkout_path, $filename), $encoding, $search, $replace );
	}
}

sub inject_revision
{
	my $versions_ref = shift;
	my %versions = %$versions_ref;
	my $search = '(FS_VERSION_REVIS |,|\.)' . $versions{lastreleaserevision};
	my $replace = '${1}' . $versions{nextreleaserevision};
	$raw_regex = 1;

	return ($search, $replace);
}

sub replace_revision_periods
{
	my $versions_ref = shift;
	my %versions = %$versions_ref;
	my $search = $versions{lastversion} . "." . $versions{lastreleaserevision};
	my $replace = $versions{nextversion} . "." . $versions{nextreleaserevision};

	return ($search, $replace);
}

sub replace_revision_commas
{
	my ($search, $replace) = Replacer::replace_revision_periods(shift);
	$search =~ s/\./,/g;
	$replace =~ s/\./,/g;

	return ($search, $replace);
}

sub replace_version_major
{
	my $versions_ref = shift;
	my %versions = %$versions_ref;
	my ($lastmajor, $lastminor, $lastbuild) = split(/\./, $versions{lastversion});
	my ($nextmajor, $nextminor, $nextbuild) = split(/\./, $versions{nextversion});
	my $search = "FS_VERSION_MAJOR " . $lastmajor;
	my $replace = "FS_VERSION_MAJOR " . $nextmajor;

	return ($search, $replace);
}

sub replace_version_minor
{
	my $versions_ref = shift;
	my %versions = %$versions_ref;
	my ($lastmajor, $lastminor, $lastbuild) = split(/\./, $versions{lastversion});
	my ($nextmajor, $nextminor, $nextbuild) = split(/\./, $versions{nextversion});
	my $search = "FS_VERSION_MINOR " . $lastminor;
	my $replace = "FS_VERSION_MINOR " . $nextminor;

	return ($search, $replace);
}

sub replace_version_build
{
	my $versions_ref = shift;
	my %versions = %$versions_ref;
	my ($lastmajor, $lastminor, $lastbuild) = split(/\./, $versions{lastversion});
	my ($nextmajor, $nextminor, $nextbuild) = split(/\./, $versions{nextversion});
	my $search = "FS_VERSION_BUILD " . $lastbuild;
	my $replace = "FS_VERSION_BUILD " . $nextbuild;

	return ($search, $replace);
}

sub replace_version_revision
{
	my $versions_ref = shift;
	my %versions = %$versions_ref;
	my $search = "FS_VERSION_REVIS " . $versions{lastreleaserevision};
	my $replace = "FS_VERSION_REVIS " . $versions{nextreleaserevision};

	return ($search, $replace);
}

sub replace_natural_version
{
	my $versions_ref = shift;
	my %versions = %$versions_ref;
	my $search = $versions{lastversion};
	my $replace = $versions{nextversion};

	if($versions{lastsubversion})
	{
		$search .= " " . $versions{lastsubversion};
	}

	if($versions{nextsubversion})
	{
		$replace .= " " . $versions{nextsubversion};
	}

	return ($search, $replace);
}

sub replace_spaces_only
{
	my ($search, $replace) = Replacer::replace_natural_version(shift);
	$search =~ s/\ /_/g;
	$replace =~ s/\ /_/g;

	return ($search, $replace);
}

sub replace_msvc_version
{
	my ($search, $replace) = Replacer::replace_natural_version(shift);
	$search =~ s/[\.\ ]/_/g;
	$search = "2_open_" . $search;
	$replace =~ s/[\.\ ]/_/g;
	$replace = "2_open_" . $replace;

	return ($search, $replace);
}

sub replace_msvc2008_tts
{
	my $versions_ref = shift;
	my %versions = %$versions_ref;
	my $search = '_SECURE_SCL=0;_HAS_ITERATOR_DEBUGGING=0;"';
	my $replace = '_SECURE_SCL=0;_HAS_ITERATOR_DEBUGGING=0;FS2_SPEECH;FS2_VOICER;"';

	return ($search, $replace);
}

sub replace_msvc2008_voicer
{
	my $versions_ref = shift;
	my %versions = %$versions_ref;
	my $search = '_VC08;';
	my $replace = '_VC08;FS2_VOICER;';

	return ($search, $replace);
}

sub replace_in_file
{
	my ($filename, $encoding, $search, $replace) = @_;

	my $data = Replacer::read_file($filename, $encoding);
	unless($raw_regex)
	{
		$search = "\Q$search\E";
	}
	$replace =~ s/\"/\\\"/g;
	$replace = '"' . $replace . '"';
	$data =~ s/$search/$replace/gee;

	Replacer::write_file($filename, $encoding, $data);
}

sub read_file {
	my ($filename, $encoding) = @_;
	
	open my $in, '<:' . $encoding, $filename or die "Could not open '$filename' for reading $!";
	local $/ = undef;
	my $all = <$in>;
	close $in;
	
	return $all;
}
 
sub write_file {
	my ($filename, $encoding, $content) = @_;

	open my $out, '>:' . $encoding, $filename or die "Could not open '$filename' for writing $!";;
	print $out $content;
	close $out;

	return;
}

1;
