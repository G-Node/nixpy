import argparse


def main():
    parser = argparse.ArgumentParser(
        description="Upgrade NIX files to newest version"
    )
    parser.add_argument("-f", "--force", action="store_true",
                        help="overwrite existing files without prompting")
    parser.add_argument("file", type=str, nargs="+",
                        help="path to file to upgrade (at least one)")
    args = parser.parse_args()
    files = args.file

    print(f"Upgrading {len(files)} files...")


if __name__ == "__main__":
    main()
