import pathlib

from .utils import EntryPoint, RosPackageXml


def is_directory_only_contain(directory: pathlib.Path, name: str):
    if directory.exists():
        if [path.name for path in directory.iterdir()] != [name]:
            print(f"'{directory}' should only contain '{name}' directory")
            return False
    return True


def process_file(path: pathlib.Path, args):
    package = RosPackageXml(path).get_name(include_prefix=False)
    include = path.with_name("include")
    autoware = "autoware"
    if not is_directory_only_contain(include, autoware):
        return 1
    if not is_directory_only_contain(include.joinpath(autoware), package):
        return 1
    return 0


def main(argv=None):
    return EntryPoint().main(process_file, argv)
