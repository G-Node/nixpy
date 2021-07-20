"""
Command line interface for nixio tools.

  nixio explore:  Print file information, data, or metadata, with support for
                  filtering and plotting.
  nixio validate: Check NIX files for missing or inconsistent objects and
                  annotations.
  nixio upgrade:  Update older files to the newest file format.
"""
import sys
import argparse
from . import explore, validate, upgrade


def main():
    parser = argparse.ArgumentParser(
        description="Command line interface for nixio tools"
    )
    if sys.version_info.major < 3 or sys.version_info.minor < 6:
        raise RuntimeError("nixio does not support python versions less than 3.6!")
    if sys.version_info.minor < 7:
        subcmds = parser.add_subparsers(title="commands", dest="cmd")
    else:
        subcmds = parser.add_subparsers(title="commands", required=True,
                                        dest="cmd")

    # nixio explore
    explore_cmd = subcmds.add_parser("explore", help=explore.__doc__)
    explore.create_subcmd_parsers(explore_cmd)

    # nixio validate
    validate_cmd = subcmds.add_parser("validate", help=validate.__doc__)
    validate.create_subcmd_parser(validate_cmd)

    # nixio upgrade
    upgrade_cmd = subcmds.add_parser("upgrade", help=upgrade.__doc__)
    upgrade.create_subcmd_parser(upgrade_cmd)

    cmdmap = {
        "explore": explore.main,
        "validate": validate.main,
        "upgrade": upgrade.main
    }

    args = parser.parse_args()
    cmd = args.cmd
    cmdmap[cmd](args)


if __name__ == "__main__":
    main()
