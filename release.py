#!/bin/env python3

import argparse
import os
import sys

import git
import semantic_version
import yaml

from util import expand_config_vars

# Assumes git has SirKnightly credentials already
def main():
    # Set up paths
    print("Setting up paths...")
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)

    # Parse the command line arguments
    print("Parsing cmdline...")
    parser = argparse.ArgumentParser()
    parser.add_argument("--config",     help="Sets the config file", default="config.yml")
    parser.add_argument("--version",    help="The version to mark this release as")
    parser.add_argument("--type",       help="Either \'candidate\', \'release\', \'point_release_candidate\', or \'point_release\'")
    parser.add_argument("--candidate",  help="This specifies the candidate number.  It is ignored if --type = \'release\' or \'point_release\'",
        type=int)

    args = parser.parse_args()

    # Read in configuration data from config.yml
    print("Parsing config.yml...")
    config = {}

    with open(args.config, "r") as f:
        try:
            config = yaml.safe_load(f)
            # Support some variables in the config
            expand_config_vars(config)
        except yaml.YAMLError as e:
            print(e)
            sys.exit(1)

    # Validate version
    print("Validating version...")
    if not semantic_version.validate(args.version):
        print("Error: Specified version is not a valid version string!")
        sys.exit(1)

    # Validate type and candidate
    print("Validating type...")
    if (args.type == "candidate" or args.type == "point_release_candidate"):
        if (not isinstance(args.candidate, int)) or (args.candidate < 0):
            print ("Error: Candidate field must be a non-negative integer!")
            sys.exit(1)
            
    elif (args.type != "release" and args.type != "point_release"):
        print("Error: unknown release type \'{}\'!".format(args.type))
        sys.exit(1)

    print("Resolving target branch -- NOTE! Point Releases are hardcoded to this branch name format: pr_<major>_<minor>_<patch>")
    version = semantic_version.Version(args.version)

    if (args.type == "point_release" or args.type == "point_release_candidate"):
        branch = "pr_{}_{}_{}".format(version.major, version.minor, version.patch)
    else:
        branch = config["git"]["branch"]

    # Checkout repo
    print("Checking out repo: {}/{}".format(config["git"]["repo"], branch))
    repo = git.GitRepository(config["git"]["repo"], branch)
    repo.update_repository()

    # Form tag string according to type
    print("Forming tag name...")
    tag_name = ''
    if (args.type == "candidate" or args.type == "point_release_candidate"):
        # suffix RC# to version
        version.prerelease = "RC{}".format(args.candidate)
        tag_name = "release_{}_{}_{}-{}".format(version.major, version.minor, version.patch, version.prerelease)

    elif (args.type == "release" or args.type == "point_release"):
        # no suffix
        version.prerelease = ""
        tag_name = "release_{}_{}_{}".format(version.major, version.minor, version.patch)

    print("  tag: {}".format(tag_name))

    # Configure version_override.cmake for proper in-game version ident
    with open(os.path.join(config["git"]["repo"], "version_override.cmake"), "w") as f:
        f.write("set(FSO_VERSION_MAJOR {})\n".format(version.major))
        f.write("set(FSO_VERSION_MINOR {})\n".format(version.minor))
        f.write("set(FSO_VERSION_BUILD {})\n".format(version.patch))
        f.write("set(FSO_VERSION_REVISION 0)\n")
        f.write("set(FSO_VERSION_REVISION_STR {})\n".format(version.prerelease))

    print("  version_override.cmake created!")

    # Check if tag name already exists
    print("Checking if tag name exists...")
    latest_tag = repo.get_latest_tag_name("release_*")
    if tag_name == latest_tag:
        print("Error: Tag with name of \'{}\' already exists!".format(tag_name))
        sys.exit(1)

    # Commit the version_override.cmake, if any, and create an annotated tag to trigger the release_build.yml in the main repo
    print("Commit, tag, and push...")
    repo.commit_and_tag(tag_name)

    print("Done!")

if __name__ == "__main__":
    main()
