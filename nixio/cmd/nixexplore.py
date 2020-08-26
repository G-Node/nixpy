"""
Search for information within NIX file(s). Use the "file" command for
general information about the file(s). The verbose flag can be used to get
more detailed information about the file structure. Multiple -v options
increase the verbosity.
(e.g.  'nixio explore file nix_file -vvv' for most detailed output).

The "metadata" (mdata) and "data" commands provide further options for finding
and viewing data and metadata information. With the "dump" subcommand data can
be dumped to file (up to 3D data).

The "plot" command is only available if the nixworks package is installed
(https://github.com/G-node/nixworks).

NOTE: This tool is under active development. Please use the github issue
tracker (https://github.com/G-node/nixpy/issues) for bug reports and feature
requests.
"""
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

general_help = """ Search for information within NIX file(s). Use the \"file\" 
command for general information about the file(s). The verbosity flag can be used to 
get more detailed information about the file structure. (e.g.
 \'nixio-explore file nix_file -vvv\' for most detailed output).

The \"metadata\" (mdata) and \"data\" commands provide further options for finding and viewing data
and metadata information. With the \"dump\" subcommand data can be dumped to file (up to 3D data).
The plot command is only available if the nixworks package is installed (https://github.com/G-node/nixworks).
\n\n Note that this tool is not yet fully implemented. Please use the github issue tracker 
(https://github.com/G-node/nixpy/issues) for bug reports and feature requests.""".strip()

tool_description = """
nixio-explore functionality is split into sub-commands for file, metadata, and data exploration. For 
help on the commands type e.g.: 'nixio-explore file --help'.
"""

mdata_pattern_help = """
Pattern(s) with which to look for sections and properties. The
pattern can be either
1) type_or_name: First looks for a section
matching in type or name or a property with matching name.
2) type_or_name/prop_name: first looks for a matching section and within
those for matching properties.
Patterns are applied case-insensitive
and can be partial matches. You can provide multiple patterns by calling the command like: `nixio-explore metadata -p "subject" -p "species" file1.nix file2.nix`
""".strip()

data_parser_help = """
Display information about data entities such as DataArrays, Tags, or MultiTags. 
""".strip()

data_pattern_help = """
A string pattern that is parsed to find the data entity.
""".strip()

dump_parser_help = """
Dump data to stdout. This command can process up to 3D data. The data dump contains 
dimension information as well as the stored data. To write the data to  text file use e.g. 
\'nixio-explore dump path_to_nix_file -p \"name or type of data entity\" > data.dump\' or provide the \"--outfile\" argument. 
""".strip()

dump_pattern_help = data_pattern_help

dump_outfile_help = """
Name of a file into which the data should be dumped. If not given data will be dumped to stdout.
""".strip()

plot_parser_help = """
Create basic plots of the stored data. This command is only available if nixworks is installed.
""".strip()

def progress(count, total, status='', bar_len=60):
    """
    modified after https://gist.github.com/vladignatyev/06860ec2040cb497f0f3
    by Vladimir Ignatev published under MIT License
    """
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
                print("Error: invalid file or directory! No matches found. '{}'".format(filename))
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
                                                                       frames, groups, tags, mtags,
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
    for block in nix_file.blocks:
        for cls in classes:
            for entity in getattr(block, cls):
                ename = entity.name() if arguments.case_sensitive else entity.name.lower()
                etype = entity.type() if arguments.case_sensitive else entity.type.lower()
                if arguments.full_match:
                    if ename == name_or_type or etype == name_or_type:
                        entities.append(entity)
                else:
                    if name_or_type in ename or name_or_type in etype:
                        entities.append(entity)
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


def get_dim_label_and_unit(dimension):
    dim_label = getattr(dimension, "label") if hasattr(dimension, "label") and getattr(dimension, "label") else ""
    dim_unit = getattr(dimension, "unit") if hasattr(dimension, "unit") and getattr(dimension, "unit") else ""
    return dim_label, dim_unit


def dump_oned(data, dimension, label, unit, outfile, format="%.6f", end="\n\n", forgiving=True, show_progress=False):
    if len(data.shape) > 1:
        raise ValueError("data dimensionality is too deep, expected 1D data, got %iD" % len(data.shape))
    ticks = get_ticks(dimension, data.shape[0])
    if len(ticks) != len(data):
        if not forgiving:
            print("Cannot dump data, could not read the dimension values on dimension %i (type: %s)!" % (dimension.index, dimension.dimension_type))
            return
        else:
            ticks = np.arange(len(data))
    dim_label, dim_unit = get_dim_label_and_unit(dimension)
    if isinstance(ticks[-1], str):
        max_tick_len = max([len(ticks[-1]), len(dim_label)])
    else:
        max_tick_len = max([len(format % ticks[-1]), len(dim_label)])

    numeric_dim_ticks = isinstance(ticks[0], (int, float))
    numeric_data = isinstance(data[0], (int, float))
    data_conv_func = (lambda x: format % x) if numeric_data else str
    dim_ticks_conv_func = (lambda x: format % x) if numeric_dim_ticks else str

    if dimension.dimension_type == nix.DimensionType.Range and dimension.has_link:
        print("# %s" % dim_label, file=outfile)
        print("# %s" % dim_unit, file=outfile)
        for i, t in enumerate(ticks):
            print(data_conv_func(t), file=outfile)
            if show_progress and i % 1000 == 0:
                progress(i, data.shape[0], status='')
    else:
        padding = " " * (max_tick_len - len(dim_label) if dim_label else 0)
        print("# %s%s%s" % (dim_label, padding, label), file=outfile)
        padding = " " * (max_tick_len - len(dim_unit) if dim_unit else 0)
        print("# %s%s%s" % (dim_unit, padding, unit), file=outfile)

        for i in range(data.shape[0]):
            if show_progress and i % 1000 == 0:
                progress(i, data.shape[0], status='')
            print(dim_ticks_conv_func(ticks[i]) + "   " + data_conv_func(data[i]), file=outfile)
    if show_progress:
        progress(data.shape[0], data.shape[0], "Done")
    print(end, file=outfile)


def dump_twod(data, dimensions, label, unit, outfile, format="%.6f", end="\n\n", show_progress=False):
    if len(data.shape) != 2 or len(dimensions) != 2:
        raise ValueError("data must be 2 dimensional and exactly two dimensions must be passed inorder to dump the content properly.")
    first_dim_ticks = get_ticks(dimensions[0], data.shape[0])
    second_dim_ticks = get_ticks(dimensions[1], data.shape[1])
    if len(first_dim_ticks) != data.shape[0] or len(second_dim_ticks) != data.shape[1]:
        raise ValueError("dimension ticks for first or second dimension do not match the data shape.")

    first_dim_label, first_dim_unit = get_dim_label_and_unit(dimensions[0])
    second_dim_label, second_dim_unit = get_dim_label_and_unit(dimensions[1])

    numeric_1st_dim_ticks = isinstance(first_dim_ticks[0], (int, float))
    numeric_2nd_dim_ticks = isinstance(second_dim_ticks[0], (int, float))
    numeric_data = isinstance(data[0, 0], (int, float))
    data_conv_func = (lambda x: format % x) if numeric_data else str
    dim_ticks_conv_func1 = (lambda x: format % x) if numeric_1st_dim_ticks else str
    dim_ticks_conv_func2 = (lambda x: format % x) if numeric_2nd_dim_ticks else str

    max_tick_len = max([len(dim_ticks_conv_func1(first_dim_ticks[-1])), len(first_dim_label)])
    print("# data label: %s" % label, file=outfile)
    print("# data unit: %s\n" % unit, file=outfile)
    padding = " " * (max_tick_len - (len(first_dim_label) if first_dim_unit else 0))
    print("# %s%s%s" % (first_dim_label, padding, second_dim_label), file=outfile)
    padding = " " * (max_tick_len - (len(first_dim_unit) if first_dim_unit else 0))
    print("# %s%s%s" % (first_dim_unit, padding, second_dim_unit), file=outfile)
    # first line contains 2nd dim ticks
    print(" " * max_tick_len + "   " + (" " * max_tick_len + "  ").join(map(dim_ticks_conv_func2, second_dim_ticks)), file=outfile)
    # now dump the rest
    for i in range(len(first_dim_ticks)):
        print(dim_ticks_conv_func1(first_dim_ticks[i]) + "    " + "   ".join(map(data_conv_func, data[i, :])), file=outfile)
        if show_progress and i % 500 == 0:
            progress(i, data.shape[0], status='')
    if show_progress:
        progress(data.shape[0], data.shape[0], "Done")
    print(end, file=outfile)


def dump_threed(data, dimensions, label, unit, outfile, format="%.6f", end="\n\n", show_progress=False):
    if len(data.shape) != 3 or len(dimensions) != 3:
        raise ValueError("data must be 3 dimensional and exactly three dimensions must be passed inorder to dump the content properly.")
    ticks = get_ticks(dimensions[2], data.shape[2])
    dim_label, dim_unit = get_dim_label_and_unit(dimensions[2])

    for i in range(data.shape[2]):
        print("# data[:, :, %i]: %s" % (i, dim_label + "%s%s" % (ticks[i], dim_unit) if dim_unit else ""), file=outfile)
        dump_twod(data[:, :, i], [dimensions[0], dimensions[1]], label, unit, outfile, format, end="\n", show_progress=show_progress)

    print(end, file=outfile)


def dump_data_array(array, filename, outfile, show_progress=False):
    print("# File: %s\n# entity: %s\n# type: %s\n# id: %s" % (filename, array.name, array.type, array.id), file=outfile)
    print("# created at: %s\n# last edited at: %s\n" %
          (str(dt.datetime.fromtimestamp(array.created_at)),
           str(dt.datetime.fromtimestamp(array.updated_at))), file=outfile)
    dims = len(array.shape)
    data = array[:]
    if dims == 1:
        dump_oned(data, array.dimensions[0], array.label, array.unit, outfile, show_progress=show_progress)
    elif dims == 2:
        dump_twod(data, array.dimensions, array.label, array.unit, outfile, show_progress=show_progress)
    elif dims == 3:
        dump_threed(data, array.dimensions, array.label, array.unit, outfile, show_progress=show_progress)
    else:
        print("Sorry, cannot dump data with more than 3 dimensions!")


def data_dump(filename, arguments, outfile, show_progress=False):
    nix_file = open_nix_file(filename)
    entities = find_data_entity(nix_file, arguments)
    for e in entities:
        if isinstance(e, nix.DataArray):
            sys.stderr.write("Dumping %s to %s...\n" % (e.name, arguments.outfile))
            dump_data_array(e, filename, outfile, show_progress)
            sys.stderr.write("\n")
    nix_file.close()


def data_plotter(filename, arguments):
    nix_file = open_nix_file(filename)
    entities = find_data_entity(nix_file, arguments)
    for e in entities:
        if isinstance(e, nix.DataArray):
            plotter = nw.plotter.suggested_plotter(e)
            if plotter:
                plotter.plot()
                plotter.show()
            else:
                print("Could not find a suitable plotter for the DataArray: %s" % str(e))
        else:
            print("Sorry, so far I can only try to plot DataArrays.")

    nix_file.close()


def disp_data(filename, arguments):
    nix_file = open_nix_file(filename)
    entities = find_data_entity(nix_file, arguments)
    print("# File: %s" % filename)
    for e in entities:
        print("# entity: %s\n# type: %s\n# id: %s" % (e.name, e.type, e.id))
        print("# created at: %s\n# last edited at: %s\n" %
              (str(dt.datetime.fromtimestamp(e.created_at)),
               str(dt.datetime.fromtimestamp(e.updated_at))))
        print(e)
        print("\n")
    nix_file.close()


def data_worker(arguments):
    files = assemble_files(arguments)
    for nf in files:
        disp_data(nf, arguments)


def file_worker(arguments):
    files = assemble_files(arguments)
    for nf in files:
        disp_file_info(nf, arguments)


def dump_worker(arguments):
    files = assemble_files(arguments)
    func = data_dump
    if len(arguments.outfile) > 0:
        if os.path.exists(arguments.outfile):
            response = input("File %s already exists, are you sure to overwrite it? y/N:" % arguments.outfile)
            if response.lower() != "y":
                print("... data dump aborted.")
                return
        f = open(arguments.outfile, 'w')
        to_file = True
    else:
        f = sys.stdout
        to_file = False
    show_progress = to_file
    for nf in files:
        func(nf, arguments, f, show_progress)
    if to_file:
        f.close()


def plot_worker(arguments):
    files = assemble_files(arguments)
    func = data_plotter
    for nf in files:
        func(nf, arguments)


def add_default_file_args(parent_parser):
    parent_parser.add_argument("file", type=str, nargs="+",
                               help="Path to file (at least one)")
    parent_parser.add_argument("-s", "--suffix", type=str, default="nix", nargs="?",
                               help="The file suffix used for nix data files (default: %(default)s).")


def add_default_args(parent_parser):
    parent_parser.add_argument("-c", "--case_sensitive", action="store_true", help="matching of"
                               + " entitiy names and types is case sensitive, by default the case is ignored")
    parent_parser.add_argument("-fm", "--full_match", action="store_true", help="names and types must"
                               + " be full matches, bey default a partial match is sufficient")


def create_metadata_parser(parent_parser):
    meta_parser = parent_parser.add_parser("metadata", help="Filter and display metadata", aliases=["mdata"],
                                           description="Search for metadata items or display metadata (sub)trees.")
    meta_parser.add_argument("-p", "--pattern", type=str, action="append", help=mdata_pattern_help)
    meta_parser.add_argument("-d", "--depth", type=int, default=-1,
                             help="maximum depth of metadata tree output, default is %(default)s, full depth")
    add_default_args(meta_parser)
    add_default_file_args(meta_parser)
    meta_parser.set_defaults(func=mdata_worker)
    # add value search?
    # add option to specify directly if one looks for a property which would increase performance


def create_data_parser(parent_parser):
    data_parser = parent_parser.add_parser("data", help="Search and display information about data entities",
                                           description=data_parser_help)
    data_parser.add_argument("-p", "--pattern", default="", type=str, help=data_pattern_help)
    add_default_args(data_parser)
    add_default_file_args(data_parser)
    data_parser.set_defaults(func=data_worker)


def create_dump_parser(parent_parser):
    dump_parser = parent_parser.add_parser("dump", help="Dump stored data to stdout",
                                           description=dump_parser_help)
    dump_parser.add_argument("-p", "--pattern", default="", type=str, help=dump_pattern_help)
    dump_parser.add_argument("-o", "--outfile", default="", type=str, help=dump_outfile_help)
    add_default_args(dump_parser)
    add_default_file_args(dump_parser)
    dump_parser.set_defaults(func=dump_worker)


def create_plot_parser(parent_parser):
    if not nw_present:
        return
    plot_parser = parent_parser.add_parser("plot", help="Create basic plots of stored data.",
                                           description=plot_parser_help)
    plot_parser.add_argument("-p", "--pattern", type=str, help=data_pattern_help)
    add_default_args(plot_parser)
    add_default_file_args(plot_parser)
    plot_parser.set_defaults(func=plot_worker)


def create_file_parser(parent_parser):
    file_parser = parent_parser.add_parser("file", help="Display basic file info",
                                           description="Quick display of file information such as " +
                                           "creation date, file size and structure etc.")
    file_parser.add_argument("-v", "--verbosity", action="count",
                             help="increase output verbosity, use -v, -vv, -vvv for more verbose output")
    add_default_file_args(file_parser)
    file_parser.set_defaults(func=file_worker)


def create_parser():
    parser = argparse.ArgumentParser(prog="nixio-explore",
                                     description=general_help)
    subparsers = parser.add_subparsers(title="commands",
                                       help="Sub commands for working on data and metadata",
                                       description=tool_description, dest="func")

    create_file_parser(subparsers)
    create_data_parser(subparsers)
    create_dump_parser(subparsers)
    create_metadata_parser(subparsers)
    create_plot_parser(subparsers)

    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()
    if not args.func:
        parser.print_help()
        sys.exit(1)
    args.func(args)


if __name__ == "__main__":
    main()
