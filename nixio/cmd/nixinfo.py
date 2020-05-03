import os
import argparse
import nixio as nix
import glob
from IPython import embed

def open_nix_file(filename):
    f = None
    try:
        f = nix.File.open(filename, nix.FileMode.ReadOnly)
    except Exception as e:
        print("ERROR: '{}' is not a valid NIX file!\n\t error message was: '{}'".format(filename, e))
    return f


def assemble_files(arguments):
    filenames = sorted(arguments.file)
    all_files = []
    for nix_file in filenames:
        if os.path.isdir(nix_file):
            nix_file += "*." + arguments.suffix
        all_files.extend(sorted(glob.glob(nix_file)))
    return all_files


def disp_file_info(filename, arguments):
    f = open_nix_file(filename)
    if f is None:
        pass

    print(" File: %s" % (filename.split(os.sep)[-1]))
    print("\t format: %s \t version: %s " % (f.format, f.version))
    print("\t created at: %i \t last updated %i\n\n" %
          (f.created_at, f.updated_at))
    f.close()


def disp_metadata(filename, arguments):
    f = open_nix_file(filename)
    if f is None:
        pass
    print(" File: %s" % (filename.split(os.sep)[-1]))
    for sec in f.sections:
        sec.pprint(max_depth=arguments.depth)
    print("\n\n")
    f.close()


def mdata_worker(arguments):
    files = assemble_files(arguments)
    for nf in files:
        disp_metadata(nf, arguments)


def disp_data(filename, arguments):
    pass


def data_worker(arguments):
    files = assemble_files(arguments)
    for nf in files:
        disp_data(nf, arguments)


def file_worker(arguments):
    files = assemble_files(arguments)
    for nf in files:
        disp_file_info(nf, arguments)
    pass


def __create_parser():
    # create main parser
    parser = argparse.ArgumentParser(prog="nixo-info",
                                     description="Search for information within NIX file(s)")

    subparsers = parser.add_subparsers(title="commands",
                                       help="subcommands for working on data and metdata",
                                       description="Allowed subcommands")

    # parser for metadata subcommand options
    meta_parser = subparsers.add_parser("metadata", help="filter and display metadata",
                                        aliases=["m"])
    meta_parser.add_argument("-p", "--pattern", type=str, default="",
                             help="pattern(s) of sections and properties")
    meta_parser.add_argument("-d", "--depth", type=int, default=-1,
                             help="maximum depth, of metadata tree output")
    meta_parser.add_argument("file", type=str, nargs="+",
                             help="Path to file (at least one)")
    meta_parser.add_argument("-s", "--suffix", type=str, default="nix", nargs="?",
                             help="The file suffix used for nix data files (default: nix).")
    meta_parser.set_defaults(func=mdata_worker)

    # parser for data subcommand options
    data_parser = subparsers.add_parser("data", help="search and display data entities",
                                        aliases=["d"])
    data_parser.add_argument("-t", "--type", help="entity type")
    data_parser.add_argument("file", type=str, nargs="+",
                             help="Path to file (at least one)")
    data_parser.add_argument("-s", "--suffix", type=str, default="nix", nargs="?",
                             help="The file suffix used for nix data files (default: nix).")
    data_parser.set_defaults(func=data_worker)

    # parser for file subcommand options
    file_parser = subparsers.add_parser("file", help="display basic file info",
                                        aliases=["f"])
    file_parser.add_argument("file", type=str, nargs="+",
                             help="Path to file (at least one)")
    file_parser.add_argument("-s", "--suffix", type=str, default="nix", nargs="?",
                             help="The file suffix used for nix data files (default: nix).")
    file_parser.set_defaults(func=file_worker)

    return parser


def main():
    parser = __create_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
