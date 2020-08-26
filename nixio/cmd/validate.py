"""
Validate NIX files for missing or inconsistent objects and annotations.
"""
import os
import argparse
import nixio as nix


def format_obj(obj):
    return "{} '{}' (ID: {})".format(type(obj).__name__, obj.name, obj.id)


def print_header(text, h=1):
    print("  {}".format(text))
    print("  " + "-"*len(text))


def validate(filename):
    nf = nix.File(filename, mode=nix.FileMode.ReadOnly)
    results = nf.validate()
    print("Results for '{}'".format(filename))
    errors = results["errors"]
    if errors:
        plural = "s" if len(errors) > 1 else ""
        print_header("{} object{} with errors".format(len(errors), plural))
        for idx, (obj, messages) in enumerate(errors.items()):
            print(" [{}] {}".format(idx+1, format_obj(obj)))
            for msg in messages:
                print("    {}".format(msg))

    warnings = results["warnings"]
    if warnings:
        plural = "s" if len(warnings) > 1 else ""
        print_header("{} object{} with warnings".format(len(warnings), plural))
        for idx, (obj, messages) in enumerate(warnings.items()):
            print(" [{}] {}".format(idx+1, format_obj(obj)))
            for msg in messages:
                print("    {}".format(msg))

    print()


def create_subcmd_parser(parser):
    parser.add_argument("file", type=str, nargs="+",
                        help="path to file to validate (at least one)")
    return parser


def main(args):
    filenames = args.file

    for nixfn in filenames:
        if os.path.exists(nixfn):
            validate(nixfn)
        else:
            print("error: No such file '{}'".format(nixfn))
