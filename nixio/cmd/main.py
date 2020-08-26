"""
Command line interface for nixio tools.

  nixio explore:  Print file information, data, or metadata, with support for
                  filtering and plotting.
  nixio validate: Check NIX files for missing or inconsistent objects and
                  annotations.
  nixio upgrade:  Update older files to the newest file format.
"""
import argparse
from . import nixexplore as explore, validate, upgrade


def main():
    parser = argparse.ArgumentParser(
        description="Command line interface for nixio tools"
    )

    subcmds = parser.add_subparsers(title="commands", required=True,
                                    dest="cmd")

    # nixio explore
    subcmds.add_parser("explore", help=explore.__doc__)

    # nixio validate
    subcmds.add_parser("validate", help=validate.__doc__)

    # nixio upgrade
    subcmds.add_parser("upgrade", help=upgrade.__doc__)

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
