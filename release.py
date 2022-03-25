#!/bin/env python3

import argparse
import os
import sys

import git
import semantic_version
import yaml

from util import expand_config_vars

def main():
    # Set up paths
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)

    # Parse the command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--config",     help="Sets the config file", default="config.yml")
    parser.add_argument("--version",    help="The version to mark this release as")
    parser.add_argument("--type",       help="Either \'candidate\' or \'release\'")
    parser.add_argument("--candidate",  help="If --type = \'candidate\', this specifies the candidate number.  Is ignored if --type = \'release\'")

    args = parser.parse_args()

    # Read in configuration data from config.yml
    config = {}

    with open(args.config, "r") as f:
        try:
            config = yaml.safe_load(f)
            # Support some variables in the config
            expand_config_vars(config)
        except yaml.YAMLError as e:
            print(e)
            sys.exit(1)

    # Checkout repo
    repo = git.GitRepository(config["git"]["repo"], config["git"]["branch"])
    repo.update_repository()

    # Parse the command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--config",     help="Sets the config file", default="config.yml")
    parser.add_argument("--version",    help="The version to mark this release as")
    parser.add_argument("--type",       help="Either \'candidate\' or \'release\'")
    parser.add_argument("--candidate",  help="If --type = \'candidate\', this specifies the candidate number.  Is ignored if --type = \'release\'")

    # args is a dict with argument names as dict keys and the argument values as dict values 
    args = parser.parse_args()

    # Read in configuration data from config.yml
    # See config.yml.sample to see dict structure
    config = {}
    with open(args.config, "r") as f:
        try:
            config = yaml.safe_load(f)
            # Support some variables in the config
            expand_config_vars(config)
        except yaml.YAMLError as e:
            print(e)
            sys.exit(1)

    # Verify version string is valid
    if not semantic_version.validate(args.version):
        print("Error: Specified version is not a valid version string!")
        sys.exit(1)

    # Form tag string according to type
    version = semantic_version.Version(args.version)
    tag_name = ''
    if (args.type == "candidate"):
        # suffix RC# to version
        if (not isinstance(args.candidate, int)) or (args.candidate < 0):
            print ("Error: Candidate field must be a non-negative integer!")
            sys.exit(1)

        tag_name = "release_{}.{}.{}_RC{}".format(version.major, version.minor, version.build, args.candidate)

        # Don't configure version_override.cmake for RC's.  They identify as the previous unstable version

    elif (args.type == "release"):
        # no suffix
        tag_name = "release_{}.{}.{}".format(version.major, version.minor, version.build)

        # Configure version_override.cmake for proper in-game version ident
        with open(os.path.join(config["git"]["repo"], "version_override.cmake"), "a") as f:
            f.write("set(FSO_VERSION_MAJOR {})\n".format(version.major))
            f.write("set(FSO_VERSION_MINOR {})\n".format(version.minor))
            f.write("set(FSO_VERSION_BUILD {})\n".format(version.patch))
            f.write("set(FSO_VERSION_REVISION 0)\n")
            f.write("set(FSO_VERSION_REVISION_STR {})\n".format("-".join(version.prerelease)))

    else:
        print("Error: unknown release type \'{}\'!")
        sys.exit(1)
    
    # Check if tag name already exists
    latest_tag = repo.get_latest_tag_name("release_*")
    if tag_name == latest_tag:
        print("Error: Tag with name of \'{}\' already exists!".format(tag_name))
        sys.exit(1)

    # Commit the version_override.cmake, if any, and create an annotated tag to trigger the release_build.yml in the main repo
    repo.commit_and_tag(tag_name)

if __name__ == "__main__":
    main()
