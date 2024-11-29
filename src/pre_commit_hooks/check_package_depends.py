import argparse
import pathlib
import re
import xml.etree.ElementTree as etree
import yaml


def iter_depend_pkgs(filepath: pathlib.Path):
    tree = etree.parse(filepath)
    root = tree.getroot()
    pkgs = set()
    for node in root:
        if node.tag.endswith("depend") or node.tag == "name":
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


def list_rviz_pkgs(filepath: pathlib.Path):
    pkgs = set()
    def traverse(nodes):
        nonlocal pkgs
        nodes = nodes if nodes else []
        nodes = nodes if type(nodes) == list else [nodes]
        for node in nodes:
            pkgs.add(node["Class"])
            if node["Class"] == "rviz_common/Group":
                traverse(node["Displays"])

    for path in filepath.parent.glob("**/*.rviz"):
        with path.open() as fp:
            data = yaml.safe_load(fp)
        traverse(data["Panels"])
        traverse(data["Visualization Manager"]["Displays"])
        traverse(data["Visualization Manager"]["Tools"])
        traverse(data["Visualization Manager"]["Views"]["Current"])
        traverse(data["Visualization Manager"]["Views"]["Saved"])

    pkgs = {pkg for pkg in pkgs if not pkg.startswith("rviz_common/")}
    pkgs = {pkg for pkg in pkgs if not pkg.startswith("rviz_default_plugins/")}

    for pkg in pkgs:
        print("    " + pkg)
    return pkgs

def main(argv = None):
    parser = argparse.ArgumentParser()
    parser.add_argument('filenames', nargs='*')
    args = parser.parse_args(argv)

    result = 0
    for filename in args.filenames:
        filepath = pathlib.Path(filename)

        depend_pkgs = iter_depend_pkgs(filepath)
        launch_pkgs = set()
        launch_pkgs |= list_launch_pkgs(filepath)

        launch_pkgs = {pkg for pkg in launch_pkgs if "$" not in pkg}
        result_pkgs = launch_pkgs - depend_pkgs

        if result_pkgs:
            result = 1
            print(filepath)
            for pkg in result_pkgs:
                print(f"  exec_depend: {pkg}")
    return result
