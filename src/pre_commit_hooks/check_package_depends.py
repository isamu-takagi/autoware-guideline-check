import argparse
import pathlib
import re
import xml.etree.ElementTree as etree


def iter_depend_pkgs(filepath: pathlib.Path):
    tree = etree.parse(filepath)
    root = tree.getroot()
    pkgs = set()
    for node in root:
        if node.tag.endswith("depend"):
            pkgs.add(node.text)
    return pkgs


def list_launch_pkgs(filepath: pathlib.Path):
    pattern = re.compile(r"\$\(find-pkg-share (.+)\)")
    pkgs = set()
    for path in filepath.parent.glob("**/*.launch.xml"):
        with path.open() as fp:
            for line in fp:
                pkgs = pkgs.union(pattern.findall(line))
    return pkgs


def main(argv = None):
    parser = argparse.ArgumentParser()
    parser.add_argument('filenames', nargs='*')
    args = parser.parse_args(argv)

    for filename in args.filenames:
        filepath = pathlib.Path(filename)

        depend_pkgs = iter_depend_pkgs(filepath)
        launch_pkgs = list_launch_pkgs(filepath)

        launch_pkgs = {pkg for pkg in launch_pkgs if "$" not in pkg}
        result_pkgs = launch_pkgs - depend_pkgs

        for pkg in result_pkgs:
            print(pkg)
