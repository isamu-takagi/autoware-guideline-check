import pathlib
import re

import yaml

from .utils import EntryPoint, RosPackageXml, RosPackageXmlEdit


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


def process_file(path: pathlib.Path, args):
    depends = set()
    depends |= list_launch_depends(path)
    depends = {pkg for pkg in depends if "$" not in pkg}
    depends = depends - list_package_depends(path)
    if depends:
        print("Fix", path)
        xml = RosPackageXmlEdit(path)
        xml.add_depend("exec_depend", depends)
        xml.write()
        return 1
    return 0


def main(argv=None):
    return EntryPoint().main(process_file, argv)
