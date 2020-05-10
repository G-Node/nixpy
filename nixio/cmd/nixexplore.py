import os
import argparse
import nixio as nix
import glob
import datetime as dt


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


def disp_file_structure(nix_file, verbosity):
    def block_content(nix_file, verbosity):
        def array_content(block, verbosity):
            def dimension_description(data_array, verbosity):
                content = ", dimensions: ["
                dd = [d.label if d.dimension_type == nix.DimensionType.Sample or
                      d.dimension_type == nix.DimensionType.Range else d.dimension_type
                      for d in data_array.dimensions]
                content += ",".join(dd)
                content += "]"
                return content

            def array_structure(data_array, verbosity):
                dims = dimension_description(data_array, verbosity)
                content = "\n       shape: %s, dtype: %s %s" % (data_array.shape, data_array.dtype, dims)
                return content

            content = ""
            for a in b.data_arrays:
                array_struct = array_structure(a, verbosity) if verbosity > 2 else ""
                content += "      %s [%s] --- id: %s    %s\n" % (a.name, a.type, a.id, array_struct)
            return content

        def group_content(block, verbosity):
            content = "      groups\n"
            return content

        def tag_content(block, verbosity):
            return "      tags\n"

        def mtag_content(block, verbosity):
            return "      mtags\n"

        def frame_content(block, verbosity):
            return "      frames\n"

        def source_content(block, verbosity):
            return "      sources\n"

        content = ""
        if verbosity < 1:
            content += "  %i block(s)" % len(nix_file.blocks)
        else:
            for b in nix_file.blocks:
                arrays = array_content(b, verbosity) if verbosity > 1 else "      %i data arrays\n" % len(b.data_arrays)
                if getattr(b, "data_frames", None) is not None:
                    frames = frame_content(b, verbosity) if verbosity > 1 else "      %i data frames\n" % len(b.data_frames)
                else:
                    frames = ""
                groups = group_content(b, verbosity) if verbosity > 1 else "      %i groups\n" % len(b.groups)
                tags = tag_content(b, verbosity) if verbosity > 1 else "      %i tags\n" % len(b.tags)
                mtags = mtag_content(b, verbosity) if verbosity > 1 else "      %i multi-tags\n" % len(b.multi_tags)
                srcs = source_content(b, verbosity) if verbosity >1 else "      %i sources\n" % len(b.sources)
                content += "    %s [%s] --- id: %s\n%s%s%s%s%s%s\n" % (b.name, b.type, b.id, arrays, frames,  groups, tags, mtags, srcs)
        return content

    def section_content(nix_file, verbosity):
        def subsections(section, verbosity):
            content = ""
            sections = s.find_sections()
            prop_count = sum([len(sec) for sec in sections])
            content += "\n     %i sub-section(s), %i properties\n" % (len(sections), prop_count)
            return content

        content = ""
        if verbosity < 1:
            content += "  %i section(s)" % len(nix_file.find_sections())
        else:
            for s in nix_file.sections:
                subs_props = "\n" if verbosity < 1 else subsections(s, verbosity)
                content += "    %s [%s] --- id: %s%s" % (s.name, s.type, s.id, subs_props)
        return content

    def file_content(nix_file, verbosity):
        if verbosity is None:
            verbosity = 0
        content = ""
        if verbosity < 1:
            content += "%s\n%s" % (block_content(nix_file, verbosity), section_content(nix_file, verbosity))
        else:
            content += "  data:\n%s" % block_content(nix_file, verbosity)
            content += "  metadata:\n%s\n" % section_content(nix_file, verbosity)
        return content

    print("\n%s" % file_content(nix_file, verbosity))


def disp_file_info(filename, arguments):
    f = open_nix_file(filename)
    if f is None:
        pass

    print(" File: %s" % (filename.split(os.sep)[-1]))
    print("  format: %s \n  version: %s " % (f.format, f.version))
    print("  created at: %s \n  last updated %s" %
          (str(dt.datetime.fromtimestamp(f.created_at)),
           str(dt.datetime.fromtimestamp(f.updated_at))))
    print("  size on disk: %2.f MB" % (os.path.getsize(filename) / 10**6))
    disp_file_structure(f, arguments.verbosity)
    f.close()


def find_section(nix_file, pattern):
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


def create_metadata_parser(parent_parser):
    meta_parser = parent_parser.add_parser("metadata", help="filter and display metadata", aliases=["m"],
                                           description="Search for metadata items or display metadata (sub)trees.")
    meta_parser.add_argument("-p", "--pattern", type=str, default=[], nargs="+",
                             help=mdata_pattern_help)
    meta_parser.add_argument("-d", "--depth", type=int, default=-1,
                             help="maximum depth of metadata tree output, default is %(default)s, full depth")
    meta_parser.add_argument("file", type=str, nargs="+",
                             help="Path to file (at least one)")
    meta_parser.add_argument("-s", "--suffix", type=str, default="nix", nargs="?",
                             help="The file suffix used for nix data files (default: %(default)s).")
    meta_parser.set_defaults(func=mdata_worker)
    # add support for limitations on name or type such as case sensitivity and full vs. partial matches
    # add value search?
    # add option to specify directly if one looks for a property which would increase performance


def create_data_parser(parent_parser):
    data_parser = parent_parser.add_parser("data", help="search and display data entities", aliases=["d"],
                                           description="display information about data or dump them to system.out.")
    data_parser.add_argument("-t", "--type", help="entity type")
    data_parser.add_argument("file", type=str, nargs="+",
                             help="Path to file (at least one)")
    data_parser.add_argument("-s", "--suffix", type=str, default="nix", nargs="?",
                             help="The file suffix used for nix data files (default: %(default)s).")
    data_parser.set_defaults(func=data_worker)
    # one could even add a subcommand for plotting, if nixworks is available?


def create_file_parser(parent_parser):
    file_parser = parent_parser.add_parser("file", help="display basic file info", aliases=["f"],
                                           description="Quick display of file information such as " +
                                           "creation date, file size and structure etc.")
    file_parser.add_argument("-v", "--verbosity", action="count",
                             help="increase output verbosity, use -v, -vv, -vvv for more verbose output")
    file_parser.add_argument("file", type=str, nargs="+",
                             help="Path to file (at least one)")
    file_parser.add_argument("-s", "--suffix", type=str, default="nix", nargs="?",
                             help="The file suffix used for nix data files (default: nix).")
    file_parser.set_defaults(func=file_worker)
    # add display of file structure, file size etc...
    # add verbosity support


def create_parser():
    parser = argparse.ArgumentParser(prog="nixio-explore",
                                     description="Search for information within NIX file(s)")
    subparsers = parser.add_subparsers(title="commands",
                                       help="subcommands for working on data and metdata",
                                       description="Allowed subcommands")

    create_metadata_parser(subparsers)
    create_data_parser(subparsers)
    create_file_parser(subparsers)

    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
