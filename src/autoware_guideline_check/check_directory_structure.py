import argparse
import pathlib

from .utils import RosPackageXml


def is_directory_only_contain(directory: pathlib.Path, name: str):
    if directory.exists():
        if [path.name for path in directory.iterdir()] != [name]:
            print(f"'{directory}' should only contain '{name}' directory")
            return False
    return True


def process_file(filepath: pathlib.Path):
    package = RosPackageXml(filepath).get_name(include_prefix=False)
    include = filepath.with_name("include")
    autoware = "autoware"
    if not is_directory_only_contain(include, autoware):
        return 1
    if not is_directory_only_contain(include.joinpath(autoware), package):
        return 1
    return 0


def execute_pre_commit(function, args):
    result = 0
    for filename in args.filenames:
        filepath = pathlib.Path(filename)
        result |= function(filepath)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("filenames", nargs="*")
    args = parser.parse_args(argv)
    return execute_pre_commit(process_file, args)
