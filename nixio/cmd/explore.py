"""
Search for information within NIX file(s). Use the "file" command for
general information about the file(s). The verbose flag can be used to get
more detailed information about the file structure. Multiple -v options
increase the verbosity.
(e.g. 'nixio explore file nix_file -vvv' for most detailed output).

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
import nixio as nix
import numpy as np
import glob
import datetime as dt
import sys

try:
    import nixworks as nw
    NIX_WORKS = True
except ImportError:
    NIX_WORKS = False

TOOL_DESCRIPTION = """
nixio explore functionality is split into sub-commands for file, metadata, and data exploration. For help on the
commands type e.g.: 'nixio explore file --help'.
"""

METADATA_PATTERN_HELP = """
Pattern(s) with which to look for sections and properties. The pattern can be either 1) type_or_name: First looks for a
section matching in type or name or a property with matching name. 2) type_or_name/prop_name: first looks for a matching
section and within those for matching properties. Patterns are applied case-insensitive and can be partial matches. You
can provide multiple patterns by calling the command like: `nixio explore metadata -p "subject" -p "species" file1.nix
file2.nix`
"""

DATA_PARSER_HELP = """
Display information about data entities such as DataArrays, Tags, or MultiTags.
"""

DATA_PATTERN_HELP = """
A string pattern that is parsed to find the data entity.
"""

DUMP_PARSER_HELP = """
Dump data to file or stdout. This command can process up to 3D data. The data dump contains dimension information as
well as the stored data. To write the data to text file use e.g. 'nixio explore dump path_to_nix_file -p "name or type
of data entity" > data.dump' or provide the "--outfile" argument.
"""

DUMP_PATTERN_HELP = DATA_PATTERN_HELP

DUMP_OUTFILE_HELP = """
Name of a file into which the data should be dumped. If not given data will be dumped to stdout.
"""

PLOT_PARSER_HELP = """
Create basic plots of the stored data. This command is only available if nixworks is installed.
"""


def progress(count, total, status='', bar_len=60):
    """
    Modified after https://gist.github.com/vladignatyev/06860ec2040cb497f0f3 by Vladimir Ignatev published under MIT
    License
    """
    percents = count / total
    filled_len = int(percents * bar_len)
    prog_bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stderr.write('[%s] %.2f%s ...%s\r' %
                     (prog_bar, percents * 100, '%', status))
    sys.stderr.flush()


def open_nix_file(filename):
    nf = None
    try:
        nf = nix.File.open(filename, nix.FileMode.ReadOnly)
    except Exception as exc:
        print("ERROR: '{}' is not a valid NIX file!\n\t error message was: '{}'".format(filename,
                                                                                        exc))
    return nf


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
                print(
                    "Error: invalid file or directory! No matches found. '{}'".format(filename))
            for candidate in candidates:
                if os.path.isdir(candidate):
                    candidate = os.sep.join(
                        (candidate, "*." + arguments.suffix))
                    all_files.extend(sorted(glob.glob(candidate)))
                elif os.path.isfile(candidate):
                    all_files.append(candidate)

    return all_files


def disp_file_structure(nix_file, verbosity):
    def block_content(nix_file, verbosity):
        def array_content(block, verbosity):
            def dimension_description(data_array, _):
                content = ", dimensions: ["
                dim_desc = [d.label if d.dimension_type == nix.DimensionType.Sample or
                            d.dimension_type == nix.DimensionType.Range else d.dimension_type
                            for d in data_array.dimensions]
                content += ",".join(dim_desc)
                content += "]"
                return content

            def array_structure(data_array, verbosity):
                dims = dimension_description(data_array, verbosity)
                content = "\n       shape: %s, dtype: %s %s" % (
                    data_array.shape, data_array.dtype, dims)
                return content

            content = "      Data Arrays:\n" if len(
                block.data_arrays) > 0 else ""
            for da in block.data_arrays:
                array_struct = array_structure(
                    da, verbosity) if verbosity > 2 else ""
                content += "      %s [%s] --- id: %s    %s\n" % (
                    da.name, da.type, da.id, array_struct)
            return content

        def group_content(block, _):
            content = "      Groups:\n" if len(block.groups) > 0 else ""
            for grp in block.groups:
                content += "      %s [%s] -- id: %s\n" % (
                    grp.name, grp.type, grp.id)
            return content

        def tag_content(block, verbosity):
            def tag_details(tag, verbosity):
                if verbosity < 3:
                    return ""

                content = "      start: %s, extent: %s" % (
                    tag.position, tag.extent)
                for ref in tag.references:
                    content += "\n       refers to -> %s" % ref.name
                for feat in tag.features:
                    content += "\n       feature in -> %s" % feat.data.name
                content += "\n"
                return content

            content = "      Tags:\n"
            for tag in block.tags:
                content += "      %s [%s] --- id: %s\n %s" % (
                    tag.name, tag.type, tag.id, tag_details(tag, verbosity))
            return content

        def mtag_content(block, verbosity):
            def tag_details(tag, verbosity):
                if verbosity < 3:
                    return ""

                content = "      start: %s, extent: %s" % (
                    tag.position[:], tag.extent[:])
                for ref in tag.references:
                    content += "\n       segment refers to -> %s" % ref.name
                for feat in tag.features:
                    content += "\n       segment feature(s) in -> %s" % feat.data.name
                content += "\n"
                return content

            content = "      Multi-Tags:\n"
            for tag in block.tags:
                content += "      %s [%s] --- id: %s\n %s" % (tag.name, tag.type, tag.id,
                                                              tag_details(tag, verbosity))
            return content

        def frame_content(block, _):
            content = "      Data frames:\n" if len(
                block.data_frames) > 0 else ""
            for df in block.data_frames:
                content += "      %s [%s] -- id: %s\n" % (
                    df.name, df.type, df.id)
            return content

        def source_content(block, _):
            content = "      Sources:\n" if len(block.groups) > 0 else ""
            for src in block.sources:
                content += "      %s [%s] -- id: %s\n" % (
                    src.name, src.type, src.id)
            return content

        content = ""
        if verbosity < 1:
            content += "  %i block(s)" % len(nix_file.blocks)
        else:
            for blk in nix_file.blocks:
                arrays = array_content(blk, verbosity) if verbosity > 1 \
                    else "      %i data arrays\n" % len(blk.data_arrays)
                if getattr(blk, "data_frames", None) is not None:
                    frames = frame_content(blk, verbosity) if verbosity > 1 \
                        else "      %i data frames\n" % len(blk.data_frames)
                else:
                    frames = ""
                groups = group_content(blk, verbosity) if verbosity > 1 \
                    else "      %i groups\n" % len(blk.groups)
                tags = tag_content(blk, verbosity) if verbosity > 1 \
                    else "      %i tags\n" % len(blk.tags)
                mtags = mtag_content(blk, verbosity) if verbosity > 1 \
                    else "      %i multi-tags\n" % len(blk.multi_tags)
                srcs = source_content(blk, verbosity) if verbosity > 1 \
                    else "      %i sources\n" % len(blk.sources)
                content += "    %s [%s] --- id: %s\n%s%s%s%s%s%s\n" % (blk.name, blk.type, blk.id, arrays, frames,
                                                                       groups, tags, mtags, srcs)
        return content

    def section_content(nix_file, verbosity):
        def subsections(section, _):
            content = ""
            sections = section.find_sections()
            prop_count = sum([len(sec) for sec in sections])
            content += "\n     %i sub-section(s), %i properties\n" % (
                len(sections), prop_count)
            return content

        content = ""
        if verbosity < 1:
            content += "  %i section(s)" % len(nix_file.find_sections())
        else:
            for section in nix_file.sections:
                subs_props = subsections(section, verbosity)
                content += "    %s [%s] --- id: %s%s" % (
                    section.name, section.type, section.id, subs_props)
        return content

    def file_content(nix_file, verbosity):
        if verbosity is None:
            verbosity = 0
        content = ""
        if verbosity < 1:
            content += "%s\n%s" % (block_content(nix_file, verbosity),
                                   section_content(nix_file, verbosity))
        else:
            content += "  data:\n%s" % block_content(nix_file, verbosity)
            content += "  metadata:\n%s\n" % section_content(
                nix_file, verbosity)
        return content

    print("\n%s\n\n" % file_content(nix_file, verbosity))


def disp_file_info(filename, arguments):
    nf = open_nix_file(filename)
    if nf is None:
        pass

    print(" File: %s" % (filename.split(os.sep)[-1]))
    print("  format: %s \n  version: %s " % (nf.format, nf.version))
    print("  created at: %s \n  last updated: %s" %
          (str(dt.datetime.fromtimestamp(nf.created_at)),
           str(dt.datetime.fromtimestamp(nf.updated_at))))
    print("  size on disk: %.2f MB" % (os.path.getsize(filename) / 10**6))
    print("  location: %s" % os.path.split(filename)[0])
    disp_file_structure(nf, arguments.verbosity)
    nf.close()


def find_section(nix_file, pattern, case_sensitive=False, full_match=False):
    def type_lambda(typ, full_match):
        if full_match:
            return lambda s: typ.lower() == s.type.lower()
        else:
            return lambda s: typ.lower() in s.type.lower()

    def name_lambda(name, full_match):
        if full_match:
            return lambda s: name.lower() == s.name.lower()
        else:
            return lambda s: name.lower() in s.name.lower()

    def name_lambda_cs(name, full_match):
        if full_match:
            return lambda s: name == s.name
        else:
            return lambda s: name in s.name

    secs = nix_file.find_sections(type_lambda(pattern, full_match))
    if len(secs) == 0:
        secs = nix_file.find_sections(name_lambda_cs(pattern, full_match) if case_sensitive
                                      else name_lambda(pattern, full_match))
    return secs


def find_props(nix_file, pattern, case_sensitive=False, full_match=False):
    name = pattern if case_sensitive else pattern.lower()
    props = {}
    for sec in nix_file.find_sections(lambda s: True):
        for prop in sec.props:
            pname = prop.name if case_sensitive else prop.name.lower()
            if name == pname if full_match else name in pname:
                if sec not in props.keys():
                    props[sec] = []
                props[sec].append(prop)
    return props


def disp_metadata(filename, arguments):
    case_sensitive = arguments.case_sensitive
    full_match = arguments.full_match
    nf = open_nix_file(filename)
    if nf is None:
        return
    print("%s: " % (filename.split(os.sep)[-1]), end="\n")
    if arguments.pattern is None or len(arguments.pattern) == 0:
        for sec in nf.sections:
            sec.pprint(max_depth=arguments.depth)
    else:
        for patt in arguments.pattern:
            if "/" in patt:
                parts = patt.split("/")
                sections = find_section(nf, parts[0], case_sensitive)
                for sec in sections:
                    for prop in sec.props:
                        part = parts[1] if case_sensitive else parts[1].lower()
                        pname = prop.name if case_sensitive else prop.name.lower()
                        if part == pname if full_match else part in pname:
                            print("[section: %s, type: %s, id: %s] >> " %
                                  (sec.name, sec.type, sec.id), end="")
                            prop.pprint()
            else:
                sections = find_section(nf, patt, case_sensitive)
                if len(sections) == 0:
                    props = find_props(nf, patt, case_sensitive)
                    for sec in props.keys():
                        for prop in props[sec]:
                            print("[section: %s, type: %s, id: %s] >> " %
                                  (sec.name, sec.type, sec.id), end="")
                            prop.pprint()
                else:
                    for sec in sections:
                        sec.pprint(max_depth=arguments.depth)

    nf.close()
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
    dim_label = getattr(dimension, "label") if hasattr(dimension, "label") \
        and getattr(dimension, "label") else ""
    dim_unit = getattr(dimension, "unit") if hasattr(dimension, "unit") \
        and getattr(dimension, "unit") else ""
    return dim_label, dim_unit


def dump_oned(data, dimension, label, unit, outfile, fmt="%.6f", end="\n\n",
              forgiving=True, show_progress=False):
    if len(data.shape) > 1:
        raise ValueError("data dimensionality is too deep, "
                         "expected 1D data, got %iD" % len(data.shape))
    ticks = get_ticks(dimension, data.shape[0])
    if len(ticks) != len(data):
        if not forgiving:
            print("Cannot dump data, could not read the dimension values on dimension "
                  "%i (type: %s)!" % (dimension.index, dimension.dimension_type))
            return
        else:
            ticks = np.arange(len(data))
    dim_label, dim_unit = get_dim_label_and_unit(dimension)
    if isinstance(ticks[-1], str):
        max_tick_len = max([len(ticks[-1]), len(dim_label)])
    else:
        max_tick_len = max([len(fmt % ticks[-1]), len(dim_label)])

    numeric_dim_ticks = isinstance(ticks[0], (int, float))
    numeric_data = isinstance(data[0], (int, float))
    data_conv_func = (lambda x: fmt % x) if numeric_data else str
    dim_ticks_conv_func = (lambda x: fmt % x) if numeric_dim_ticks else str

    if dimension.dimension_type == nix.DimensionType.Range and dimension.has_link:
        print("# %s" % dim_label, file=outfile)
        print("# %s" % dim_unit, file=outfile)
        for idx, tick in enumerate(ticks):
            print(data_conv_func(tick), file=outfile)
            if show_progress and idx % 1000 == 0:
                progress(idx, data.shape[0], status='')
    else:
        padding = " " * (max_tick_len - len(dim_label) if dim_label else 0)
        print("# %s%s%s" % (dim_label, padding, label), file=outfile)
        padding = " " * (max_tick_len - len(dim_unit) if dim_unit else 0)
        print("# %s%s%s" % (dim_unit, padding, unit), file=outfile)

        for idx in range(data.shape[0]):
            if show_progress and idx % 1000 == 0:
                progress(idx, data.shape[0], status='')
            print(dim_ticks_conv_func(ticks[idx]) + "   " + data_conv_func(data[idx]),
                  file=outfile)
    if show_progress:
        progress(data.shape[0], data.shape[0], "Done")
    print(end, file=outfile)


def dump_twod(data, dimensions, label, unit, outfile, fmt="%.6f", end="\n\n",
              show_progress=False):
    if len(data.shape) != 2 or len(dimensions) != 2:
        raise ValueError("data must be 2 dimensional and exactly two dimensions must be passed "
                         "in order to dump the content properly.")
    first_dim_ticks = get_ticks(dimensions[0], data.shape[0])
    second_dim_ticks = get_ticks(dimensions[1], data.shape[1])
    if len(first_dim_ticks) != data.shape[0] or len(second_dim_ticks) != data.shape[1]:
        raise ValueError("dimension ticks for first or second dimension "
                         "do not match the data shape.")

    first_dim_label, first_dim_unit = get_dim_label_and_unit(dimensions[0])
    second_dim_label, second_dim_unit = get_dim_label_and_unit(dimensions[1])

    numeric_1st_dim_ticks = isinstance(first_dim_ticks[0], (int, float))
    numeric_2nd_dim_ticks = isinstance(second_dim_ticks[0], (int, float))
    numeric_data = isinstance(data[0, 0], (int, float))
    data_conv_func = (lambda x: fmt % x) if numeric_data else str
    dim_ticks_conv_func1 = (lambda x: fmt %
                            x) if numeric_1st_dim_ticks else str
    dim_ticks_conv_func2 = (lambda x: fmt %
                            x) if numeric_2nd_dim_ticks else str

    max_tick_len = max(
        [len(dim_ticks_conv_func1(first_dim_ticks[-1])), len(first_dim_label)])
    print("# data label: %s" % label, file=outfile)
    print("# data unit: %s\n" % unit, file=outfile)
    padding = " " * (max_tick_len - (len(first_dim_label)
                     if first_dim_unit else 0))
    print("# %s%s%s" % (first_dim_label, padding, second_dim_label), file=outfile)
    padding = " " * (max_tick_len - (len(first_dim_unit)
                     if first_dim_unit else 0))
    print("# %s%s%s" % (first_dim_unit, padding, second_dim_unit), file=outfile)
    # first line contains 2nd dim ticks
    print(" " * max_tick_len + "   " + (" " * max_tick_len + "  ").join(map(dim_ticks_conv_func2, second_dim_ticks)),
          file=outfile)
    # now dump the rest
    for i in range(len(first_dim_ticks)):
        print(dim_ticks_conv_func1(first_dim_ticks[i]) + "    " + "   ".join(map(data_conv_func, data[i, :])),
              file=outfile)
        if show_progress and i % 500 == 0:
            progress(i, data.shape[0], status='')
    if show_progress:
        progress(data.shape[0], data.shape[0], "Done")
    print(end, file=outfile)


def dump_threed(data, dimensions, label, unit, outfile, fmt="%.6f", end="\n\n",
                show_progress=False):
    if len(data.shape) != 3 or len(dimensions) != 3:
        raise ValueError("data must be 3 dimensional and exactly three dimensions must be passed in order to dump "
                         "the content properly.")
    ticks = get_ticks(dimensions[2], data.shape[2])
    dim_label, dim_unit = get_dim_label_and_unit(dimensions[2])

    for i in range(data.shape[2]):
        print("# data[:, :, %i]: %s" % (i, dim_label + "%s%s" % (ticks[i], dim_unit)
                                        if dim_unit else ""), file=outfile)
        dump_twod(data[:, :, i], [dimensions[0], dimensions[1]], label, unit, outfile, fmt,
                  end="\n", show_progress=show_progress)

    print(end, file=outfile)


def dump_data_array(array, filename, outfile, show_progress=False):
    print("# File: %s\n# entity: %s\n# type: %s\n# id: %s" % (filename, array.name, array.type, array.id),
          file=outfile)
    print("# created at: %s\n# last edited at: %s\n" % (str(dt.datetime.fromtimestamp(array.created_at)),
                                                        str(dt.datetime.fromtimestamp(array.updated_at))),
          file=outfile)
    dims = len(array.shape)
    data = array[:]
    if dims == 1:
        dump_oned(data, array.dimensions[0], array.label, array.unit, outfile,
                  show_progress=show_progress)
    elif dims == 2:
        dump_twod(data, array.dimensions, array.label, array.unit, outfile,
                  show_progress=show_progress)
    elif dims == 3:
        dump_threed(data, array.dimensions, array.label, array.unit, outfile,
                    show_progress=show_progress)
    else:
        print("Sorry, cannot dump data with more than 3 dimensions!")


def data_dump(filename, arguments, outfile, show_progress=False):
    nix_file = open_nix_file(filename)
    entities = find_data_entity(nix_file, arguments)
    for ent in entities:
        if isinstance(ent, nix.DataArray):
            sys.stderr.write("Dumping %s to %s...\n" %
                             (ent.name, arguments.outfile))
            dump_data_array(ent, filename, outfile, show_progress)
            sys.stderr.write("\n")
    nix_file.close()


def data_plotter(filename, arguments):
    nix_file = open_nix_file(filename)
    entities = find_data_entity(nix_file, arguments)
    for ent in entities:
        if isinstance(ent, nix.DataArray):
            plotter = nw.plotter.suggested_plotter(ent)
            if plotter:
                plotter.plot()
                plotter.show()
            else:
                print(
                    "Could not find a suitable plotter for the DataArray: %s" % str(ent))
        else:
            print("Sorry, so far I can only try to plot DataArrays.")

    nix_file.close()


def disp_data(filename, arguments):
    nix_file = open_nix_file(filename)
    entities = find_data_entity(nix_file, arguments)
    print("# File: %s" % filename)
    for ent in entities:
        print("# entity: %s\n# type: %s\n# id: %s" %
              (ent.name, ent.type, ent.id))
        print("# created at: %s\n# last edited at: %s\n" % (str(dt.datetime.fromtimestamp(ent.created_at)),
                                                            str(dt.datetime.fromtimestamp(ent.updated_at))))
        print(ent)
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
            response = input(
                "File %s already exists, are you sure to overwrite it? y/N:" % arguments.outfile)
            if response.lower() != "y":
                print("... data dump aborted.")
                return
        out_file = open(arguments.outfile, 'w')
        to_file = True
    else:
        out_file = sys.stdout
        to_file = False
    show_progress = to_file
    for out_file in files:
        func(out_file, arguments, out_file, show_progress)
    if to_file:
        out_file.close()


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
    parent_parser.add_argument("-c", "--case_sensitive", action="store_true",
                               help=("matching of entitiy names and types is case sensitive, "
                                     "by default the case is ignored"))
    parent_parser.add_argument("-fm", "--full_match", action="store_true",
                               help="names and types must be full matches, by default a partial match is sufficient")


def create_metadata_parser(parent_parser):
    meta_parser = parent_parser.add_parser("metadata", help="Filter and display metadata",
                                           aliases=["mdata"],
                                           description="Search for metadata items or display metadata (sub)trees.")
    meta_parser.add_argument("-p", "--pattern", type=str, action="append",
                             help=METADATA_PATTERN_HELP)
    meta_parser.add_argument("-d", "--depth", type=int, default=-1,
                             help="maximum depth of metadata tree output, default is %(default)s, full depth")
    add_default_args(meta_parser)
    add_default_file_args(meta_parser)
    meta_parser.set_defaults(func=mdata_worker)
    # add value search?
    # add option to specify directly if one looks for a property which would increase performance


def create_data_parser(parent_parser):
    data_parser = parent_parser.add_parser("data",
                                           help=(
                                               "Search and display information about data entities"),
                                           description=DATA_PARSER_HELP)
    data_parser.add_argument(
        "-p", "--pattern", default="", type=str, help=DATA_PATTERN_HELP)
    add_default_args(data_parser)
    add_default_file_args(data_parser)
    data_parser.set_defaults(func=data_worker)


def create_dump_parser(parent_parser):
    dump_parser = parent_parser.add_parser(
        "dump", help="Dump stored data to stdout", description=DUMP_PARSER_HELP)
    dump_parser.add_argument(
        "-p", "--pattern", default="", type=str, help=DUMP_PATTERN_HELP)
    dump_parser.add_argument(
        "-o", "--outfile", default="", type=str, help=DUMP_OUTFILE_HELP)
    add_default_args(dump_parser)
    add_default_file_args(dump_parser)
    dump_parser.set_defaults(func=dump_worker)


def create_plot_parser(parent_parser):
    if not NIX_WORKS:
        return
    plot_parser = parent_parser.add_parser("plot", help="Create basic plots of stored data.",
                                           description=PLOT_PARSER_HELP)
    plot_parser.add_argument(
        "-p", "--pattern", type=str, help=DATA_PATTERN_HELP)
    add_default_args(plot_parser)
    add_default_file_args(plot_parser)
    plot_parser.set_defaults(func=plot_worker)


def create_file_parser(parent_parser):
    file_parser = parent_parser.add_parser("file", help="Display basic file info",
                                           description=("Quick display of file information such as creation date, "
                                                        "file size and structure etc."))
    file_parser.add_argument("-v", "--verbosity", action="count",
                             help="increase output verbosity, use -v, -vv, -vvv for more verbose output")
    add_default_file_args(file_parser)
    file_parser.set_defaults(func=file_worker)


def create_subcmd_parsers(parser):
    subparsers = parser.add_subparsers(title="commands",
                                       help="Sub commands for working on data and metadata",
                                       description=TOOL_DESCRIPTION, dest="explore_cmd")
    create_file_parser(subparsers)
    create_data_parser(subparsers)
    create_dump_parser(subparsers)
    create_metadata_parser(subparsers)
    create_plot_parser(subparsers)

    return parser


def main(args):
    args.func(args)
