import os
import argparse
import nixio as nix
import numpy as np
import glob
import datetime as dt
import sys

try:
    import nixworks as nw
    nw_present = True
except ImportError as e:
    nw_present = False

general_help = """ Search for information within NIX file(s). Use the file sub
command for general information about the file(s) verbosity flag can be used to 
get more detailed information about the file structure. (e.g.
 \'nixio-explore file nix_file -vvv\' for most detailed output).

The metadata (m) and data (d) commands provide further options for finding and viewing.""".strip()

mdata_pattern_help = """
Pattern(s) with which to look for sections and properties. The
pattern can be either
1) type_or_name: First looks for a section
matching in type or name or a property with matching name.
2) type_or_name/prop_name: first looks for a matching section and within
those for matching properties.
Patterns are applied case-insensitive
and can be partial matches. Default: %(default)s
""".strip()

data_parser_help = """
Display information about data entities such as DataArrays, Tags, or MultiTags, or dump them to stdout. 
If the nixworks package is installed, it is also possible to plot the data. (not fully implemented yet)
""".strip()

data_pattern_help = """
A string pattern that is parsed to find the data entity.  
""".strip()


def progress(count, total, status=''):
    """
    modified after https://gist.github.com/vladignatyev/06860ec2040cb497f0f3 
    by Vladimir Ignatev published under MIT License
    """
    bar_len = 60
    percents = count / total
    filled_len = int(percents * bar_len)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stderr.write('[%s] %.2f%s ...%s\r' % (bar, percents * 100, '%', status))
    sys.stderr.flush()


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

            content = "      Data Arrays:\n" if len(block.data_arrays) > 0 else ""
            for a in b.data_arrays:
                array_struct = array_structure(a, verbosity) if verbosity > 2 else ""
                content += "      %s [%s] --- id: %s    %s\n" % (a.name, a.type, a.id, array_struct)
            return content

        def group_content(block, verbosity):
            content = "      Groups:\n" if len(block.groups) > 0 else ""
            for g in block.groups:
                content += "      %s [%s] -- id: %s\n" % (g.name, g.type, g.id)
            return content

        def tag_content(block, verbosity):
            def tag_details(tag, verbosity):
                if verbosity < 3:
                    return ""

                content = "      start: %s, extent: %s" % (tag.position, tag.extent)
                for r in tag.references:
                    content += "\n       refers to -> %s" % r.name
                for ft in tag.features:
                    content += "\n       feature in -> %s" % ft.data.name
                content += "\n"
                return content

            content = "      Tags:\n"
            for t in block.tags:
                content += "      %s [%s] --- id: %s\n %s" % (t.name, t.type, t.id, tag_details(t, verbosity))
            return content

        def mtag_content(block, verbosity):
            def tag_details(tag, verbosity):
                if verbosity < 3:
                    return ""

                content = "      start: %s, extent: %s" % (tag.position[:], tag.extent[:])
                for r in tag.references:
                    content += "\n       segment refers to -> %s" % r.name
                for ft in tag.features:
                    content += "\n       segment feature(s) in -> %s" % ft.data.name
                content += "\n"
                return content

            content = "      Multi-Tags:\n"
            for t in block.tags:
                content += "      %s [%s] --- id: %s\n %s" % (t.name, t.type, t.id, tag_details(t, verbosity))
            return content

        def frame_content(block, verbosity):
            content = "      Data frames:\n" if len(block.data_frames) > 0 else ""
            for df in block.data_frames:
                content += "      %s [%s] -- id: %s\n" % (df.name, df.type, df.id)
            return content

        def source_content(block, verbosity):
            content = "      Sources:\n" if len(block.groups) > 0 else ""
            for s in block.sources:
                content += "      %s [%s] -- id: %s\n" % (s.name, s.type, s.id)
            return content

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
                srcs = source_content(b, verbosity) if verbosity > 1 else "      %i sources\n" % len(b.sources)
                content += "    %s [%s] --- id: %s\n%s%s%s%s%s%s\n" % (b.name, b.type, b.id, arrays,
                                                                       frames,  groups, tags, mtags,
                                                                       srcs)
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
                subs_props = subsections(s, verbosity)
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

    print("\n%s\n\n" % file_content(nix_file, verbosity))


def disp_file_info(filename, arguments):
    f = open_nix_file(filename)
    if f is None:
        pass

    print(" File: %s" % (filename.split(os.sep)[-1]))
    print("  format: %s \n  version: %s " % (f.format, f.version))
    print("  created at: %s \n  last updated: %s" %
          (str(dt.datetime.fromtimestamp(f.created_at)),
           str(dt.datetime.fromtimestamp(f.updated_at))))
    print("  size on disk: %.2f MB" % (os.path.getsize(filename) / 10**6))
    print("  location: %s" % os.path.split(filename)[0])
    disp_file_structure(f, arguments.verbosity)
    f.close()


def find_section(nix_file, pattern, case_sensitive=False, full_match=False):
    def type_lambda(t, full_match):
        if full_match:
            return lambda s: t.lower() == s.type.lower()
        else:
            return lambda s: t.lower() in s.type.lower()

    def name_lambda(n, full_match):
        if full_match:
            return lambda s: n.lower() == s.name.lower()
        else:
            return lambda s: n.lower() in s.name.lower()

    def name_lambda_cs(n, full_match):
        if full_match:
            return lambda s: n == s.name
        else:
            return lambda s: n in s.name

    secs = nix_file.find_sections(type_lambda(pattern, full_match))
    if len(secs) == 0:
        secs = nix_file.find_sections(name_lambda_cs(pattern, full_match) if case_sensitive else name_lambda(pattern, full_match))
    return secs


def find_props(nix_file, pattern, case_sensitive=False, full_match=False):
    n = pattern if case_sensitive else pattern.lower()
    props = {}
    for s in nix_file.find_sections(lambda s: True):
        for p in s.props:
            pname = p.name if case_sensitive else p.name.lower()
            if n == pname if full_match else n in pname:
                if s not in props.keys():
                    props[s] = []
                props[s].append(p)
    return props


def disp_metadata(filename, arguments):
    case_sensitive = arguments.case_sensitive
    full_match = arguments.full_match
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
                secs = find_section(f, parts[0], case_sensitive)
                for s in secs:
                    for prop in s.props:
                        part = parts[1] if case_sensitive else parts[1].lower()
                        pname = prop.name if case_sensitive else prop.name.lower()
                        if part == pname if full_match else part in pname:
                            print("[section: %s, type: %s, id: %s] >> " % (s.name, s.type, s.id), end="")
                            prop.pprint()
            else:
                secs = find_section(f, p, case_sensitive)
                if len(secs) == 0:
                    props = find_props(f, p, case_sensitive)
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


def find_data_entity(nix_file, arguments):
    name_or_type = arguments.pattern if arguments.case_sensitive else arguments.pattern.lower()
    classes = ["data_arrays"]  # , "multi_tags", "tags", "data_frames"]
    entities = []
    for b in nix_file.blocks:
        for c in classes:
            for e in getattr(b, c):
                ename = e.name() if arguments.case_sensitive else e.name.lower()
                etype = e.type() if arguments.case_sensitive else e.type.lower()
                if arguments.full_match:
                    if ename == name_or_type or etype == name_or_type:
                        entities.append(e)
                else:
                    if name_or_type in ename or name_or_type in etype:
                        entities.append(e)
    return entities


def get_ticks(dimension, extent):
    ticks = None
    dim_type = dimension.dimension_type
    if dim_type == nix.DimensionType.Sample:
        ticks = np.array(dimension.axis(extent))
    elif dim_type == nix.DimensionType.Range:
        ticks = np.array(dimension.ticks)
    elif dim_type == nix.DimensionType.Set:
        ticks = np.array(dimension.labels)
        if len(ticks) == 0:
            ticks = np.arange(0., extent, 1.0)
    elif dim_type == nix.DimensionType.DataFrame:
        ticks = np.array(dimension.ticks)
    else:
        print("Unsupported dimension type!")
    return ticks


def dump_oned(data, dimension, label, unit, format="%.6f"):
    ticks = get_ticks(dimension, data.shape[0])
    dim_label = getattr(dimension, "label") if hasattr(dimension, "label") else ""
    dim_unit = getattr(dimension, "unit") if hasattr(dimension, "unit") else ""
    max_tick_len = max([len(format % ticks[-1]), len(dim_label)])
    padding = " " * (max_tick_len - len(dim_label))
    print("# %s%s%s" % (dim_label, padding, label))
    padding = " " * (max_tick_len - len(dim_unit))
    print("# %s%s%s" % (dim_unit, padding, unit))

    for i in range(data.shape[0]):
        if i % 1000 == 0:
            progress(i, data.shape[0], status='Dumping ...')

        print(format % ticks[i] + "   " + format % data[i])


def dump_data_array(array, filename):
    print("# File: %s\n# entity: %s\n# type: %s\n# id: %s" % (filename, array.name, array.type, array.id))
    print("# created at: %s\n# last edited at: %s\n" %
          (str(dt.datetime.fromtimestamp(array.created_at)),
           str(dt.datetime.fromtimestamp(array.updated_at))))
    dims = len(array.shape)
    data_view = array[:]
    if dims == 1:
        dump_oned(data_view, array.dimensions[0], array.label, array.unit)
    elif dims == 2:
        pass
    elif dims == 3:
        pass
    else:
        print("Sorry, cannot dump data with more than 3 dimensions!")
    pass


def data_dump(filename, arguments):
    nix_file = open_nix_file(filename)
    entities = find_data_entity(nix_file, arguments)
    for e in entities:
        if isinstance(e, nix.pycore.data_array.DataArray):
            dump_data_array(e, filename)

    nix_file.close()


def disp_data(filename, arguments):
    nix_file = open_nix_file(filename)
    entities = find_data_entity(nix_file, arguments)

    nix_file.close()
    pass


def data_worker(arguments):
    files = assemble_files(arguments)
    func = data_dump if arguments.dump else disp_data
    for nf in files:
        func(nf, arguments)


def file_worker(arguments):
    files = assemble_files(arguments)
    for nf in files:
        disp_file_info(nf, arguments)


def create_metadata_parser(parent_parser):
    meta_parser = parent_parser.add_parser("metadata", help="Filter and display metadata", aliases=["m"],
                                           description="Search for metadata items or display metadata (sub)trees.")
    meta_parser.add_argument("-p", "--pattern", type=str, default=[], nargs="+", help=mdata_pattern_help)
    meta_parser.add_argument("-d", "--depth", type=int, default=-1,
                             help="maximum depth of metadata tree output, default is %(default)s, full depth")
    meta_parser.add_argument("-c", "--case_sensitive", action="store_true", help="name matching of"
                             + " sections and properties is case sensitive, by default the case is ignored")
    meta_parser.add_argument("-fm", "--full_match", action="store_true", help="names and types must"
                             + " be full matches, bey default a partial match is sufficient")
    meta_parser.add_argument("file", type=str, nargs="+",
                             help="Path to file (at least one)")
    meta_parser.add_argument("-s", "--suffix", type=str, default="nix", nargs="?",
                             help="The file suffix used for nix data files (default: %(default)s).")
    meta_parser.set_defaults(func=mdata_worker)
    # add value search?
    # add option to specify directly if one looks for a property which would increase performance


def create_data_parser(parent_parser):
    data_parser = parent_parser.add_parser("data", help="Search and display data entities", aliases=["d"],
                                           description=data_parser_help)
    data_parser.add_argument("-p", "--pattern", type=str, help=data_pattern_help)
    data_parser.add_argument("-d", "--dump", help="Dump data to stdout. This functionality is limited to 3d data.",
                             action="store_true")
    data_parser.add_argument("-c", "--case_sensitive", action="store_true", help="matching of"
                             + " entitiy names and types is case sensitive, by default the case is ignored")
    data_parser.add_argument("-fm", "--full_match", action="store_true", help="names and types must"
                             + " be full matches, bey default a partial match is sufficient")
    if nw_present:
        data_parser.add_argument("-pl", "--plot", help="Plot the selected data using the generic plotting routines implemented in the nixworks package.")
        data_parser.add_argument("-i", "--interactive", action="store_true", help="Will open an interactive shell when plotting the data.")
    data_parser.add_argument("file", type=str, nargs="+",
                             help="Path to file (at least one)")
    data_parser.add_argument("-s", "--suffix", type=str, default="nix", nargs="?",
                             help="The file suffix used for nix data files (default: %(default)s).")
    data_parser.set_defaults(func=data_worker)
    # one could even add a subcommand for plotting, if nixworks is available?


def create_file_parser(parent_parser):
    file_parser = parent_parser.add_parser("file", help="Display basic file info", aliases=["f"],
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
                                     description=general_help)
    subparsers = parser.add_subparsers(title="commands",
                                       help="Sub commands for working on data and metadata",
                                       description="nixio-explore offers the following sub commands" +
                                       " for file metadata and data exploration:")

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
