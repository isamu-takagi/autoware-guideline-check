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
