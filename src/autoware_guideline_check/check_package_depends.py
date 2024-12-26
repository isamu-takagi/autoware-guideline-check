import argparse
import pathlib
import re

import yaml

from .utils.ros_package_xml import RosPackageXml, RosPackageXmlDependEditor


def list_package_depends(filepath: pathlib.Path):
    return RosPackageXml(filepath).list_package_depends()


def list_launch_depends(filepath: pathlib.Path):
    pattern = re.compile(r"\$\(find-pkg-share (.+?)\)")
    pkgs = set()
    for path in filepath.parent.glob("**/*.launch.xml"):
        with path.open() as fp:
            for line in fp:
                pkgs = pkgs.union(pattern.findall(line))
    return pkgs


def list_rviz_depends(filepath: pathlib.Path):
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


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("filenames", nargs="*")
    args = parser.parse_args(argv)

    result = 0
    for filename in args.filenames:
        filepath = pathlib.Path(filename)

        depends = set()
        depends |= list_launch_depends(filepath)
        depends = {pkg for pkg in depends if "$" not in pkg}
        depends = depends - list_package_depends(filepath)

        if depends:
            print("Fix", filepath)
            result = 1
            xml = RosPackageXmlDependEditor(filepath)
            xml.add_depend("exec_depend", depends)
            xml.write()
    return result
