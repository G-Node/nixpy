import sys
import os
import nixio as nix


def usage(cmd):
    print("Usage")
    print("  {} <nixfile>...".format(cmd))
    print()
    print("Args")
    print("  <nixfile>...    One or more NIX files")


def validate(filename):
    nf = nix.File(filename, mode=nix.FileMode.ReadOnly)
    results = nf.validate()
    print(results)


def main():
    args = sys.argv
    if len(args) < 2:
        usage(args[0])
        sys.exit(1)

    nixfnames = args[1:]
    for nixfn in nixfnames:
        if os.path.exists(nixfn):
            validate(nixfn)
        else:
            print("error: No such file '{}'".format(nixfn))


if __name__ == "__main__":
    main()
