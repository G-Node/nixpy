import os
import argparse
import nixio as nix
import glob

mdata_pattern_help = """
Pattern(s) with which to look for sections and properties. The
pattern can be either\n
1) type_or_name: First looks for a section
matching in type or name or a property with matching name.
2) type_or_name/prop_name: first looks for a matching section and within
those for matching properties.
Patterns are applied case-insensitive
and can be partial matches. Default: %(default)s
""".strip()


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
    for filename in filenames:
        if os.path.isfile(filename):
            all_files.append(filename)
        elif os.path.isdir(filename):
            filename = os.sep.join((filename, "*." + arguments.suffix))
            all_files.extend(sorted(glob.glob(filename)))
        else:
            candidates = sorted(glob.glob(filename))
            if len(candidates) == 0:
                print("Error: invalid file or directory! No matches found. '{}'").format(filename)
            for c in candidates:
                if os.path.isdir(c):
                    c = os.sep.join((c, "*." + arguments.suffix))
                    all_files.extend(sorted(glob.glob(c)))
                elif os.path.isfile(c):
                    all_files.append(c)            
            
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


def find_section(nix_file, pattern):
    # FIXME support limitations to name or type, and strictness in case
    # and full vs. partial matches 
    def type_lambda(t):
        return lambda s: t.lower() in s.type.lower()

    def name_lambda(n):
        return lambda s: n.lower() in s.name.lower()

    secs = nix_file.find_sections(type_lambda(pattern))
    if len(secs) == 0:
        secs = nix_file.find_sections(name_lambda(pattern))
    return secs


def find_props(nix_file, pattern):
    n = pattern.lower()
    props = {}
    for s in nix_file.find_sections(lambda s: True):
        for p in s.props:
            if n in p.name.lower():
                if s not in props.keys():
                    props[s] = []
                props[s].append(p)
    return props


def disp_metadata(filename, arguments):
    f = open_nix_file(filename)
    if f is None:
        pass
    print("%s: " % (filename.split(os.sep)[-1]), end="\n")
    if arguments.pattern is None or len(arguments.pattern) == 0:
        for sec in f.sections:
            sec.pprint(max_depth=arguments.depth)
    else:
        for p in arguments.pattern:
            if "/" in p:
                parts = p.split("/")
                secs = find_section(f, parts[0])
                for s in secs:
                    for prop in s.props:
                        if parts[1].lower() in prop.name.lower():
                            print("[section: %s, type: %s, id: %s] >> " % (s.name, s.type, s.id), end="")
                            prop.pprint()
            else:
                secs = find_section(f, p)
                if len(secs) == 0:
                    props = find_props(f, p)
                    for sec in props.keys():
                        for prop in props[sec]:
                            print("[section: %s, type: %s, id: %s] >> " % (sec.name, sec.type, sec.id), end="")
                            prop.pprint()
                else:
                    for s in secs:
                        s.pprint(max_depth=arguments.depth)

    f.close()
    print("\n\n")


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


def create_parser():
    # create main parser
    parser = argparse.ArgumentParser(prog="nixio-explore",
                                     description="Search for information within NIX file(s)")

    subparsers = parser.add_subparsers(title="commands",
                                       help="subcommands for working on data and metdata",
                                       description="Allowed subcommands")

    # parser for metadata subcommand options
    meta_parser = subparsers.add_parser("metadata", help="filter and display metadata",
                                        aliases=["m"])
    meta_parser.add_argument("-p", "--pattern", type=str, default=[], nargs="+",
                             help=mdata_pattern_help)
    meta_parser.add_argument("-d", "--depth", type=int, default=-1,
                             help="maximum depth of metadata tree output, default is %(default)s, full depth")
    meta_parser.add_argument("file", type=str, nargs="+",
                             help="Path to file (at least one)")
    meta_parser.add_argument("-s", "--suffix", type=str, default="nix", nargs="?",
                             help="The file suffix used for nix data files (default: %(default)s).")
    meta_parser.set_defaults(func=mdata_worker)

    # parser for data subcommand options
    data_parser = subparsers.add_parser("data", help="search and display data entities",
                                        aliases=["d"])
    data_parser.add_argument("-t", "--type", help="entity type")
    data_parser.add_argument("file", type=str, nargs="+",
                             help="Path to file (at least one)")
    data_parser.add_argument("-s", "--suffix", type=str, default="nix", nargs="?",
                             help="The file suffix used for nix data files (default: %(default)s).")
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
    parser = create_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
