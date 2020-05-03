import os
import argparse
import nixio as nix
import glob


def open_nix_file(filename):
    f = None
    try:
        f = nix.File.open(filename, nix.FileMode.ReadOnly)
    except Exception as e:
        print("ERROR: '{}' is not a valid NIX file!\n\t error message was: '{}'".format(filename, e))
    return f


def disp_file_info(filename, arguments):
    f = open_nix_file(filename)
    if f is None:
        pass

    print(" File: %s" % (filename.split(os.sep)[-1]))
    print("\t format: %s \t version: %s " % (f.format, f.version))
    print("\t created at: %i \t last updated %i" %
          (f.created_at, f.updated_at))
    f.close()


def disp_metadata(filename, arguments):
    f = open_nix_file(filename)
    if f is None:
        pass
    print(" File: %s" % (filename.split(os.sep)[-1]))
    for sec in f.sections:
        sec.pprint(max_depth=-1)

    f.close()


def worker(filename, arguments):
    if os.path.isdir(filename):
        filename += "*." + arguments.suffix
    files = glob.glob(filename)
    for file in files:
        if os.path.exists(file) and os.path.isfile(file):
            if arguments.metadata is None:
                 # and arguments.data is None:
                disp_file_info(file, arguments)
            if arguments.metadata:
                disp_metadata(file, arguments)
    pass


def main():
    parser = argparse.ArgumentParser(
        description="Search for information within NIX file(s)"
    )
    parser.add_argument("file", type=str, nargs="+",
                        help="Path to file (at least one)")
    parser.add_argument("suffix", type=str, default="nix", nargs="?", 
                        help="The suffix used for nix data files (default: nix).")
    parser.add_argument("-m", "--metadata", type=str, default="",
                        help="display file metadata, accepts a pattern")
    args = parser.parse_args()

    filenames = args.file

    for nix_file in filenames:
        worker(nix_file, args)

if __name__ == "__main__":
    main()
