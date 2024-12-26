import pathlib
import re
import xml.etree.ElementTree as etree


class RosPackageXml:
    def __init__(self, path: pathlib.Path):
        self._tree = etree.parse(path)
        self._root = self._tree.getroot()

    def get_name(self, include_prefix=True):
        name = self._root.find("name").text
        return name if include_prefix else name.removeprefix("autoware_")

    def list_package_depends(self):
        pkgs = set()
        for node in self._root:
            if node.tag.endswith("depend") or node.tag == "name":
                pkgs.add(node.text)
        return pkgs


class RosPackageXmlDependEditor:
    def __init__(self, path: pathlib.Path):
        self._path = path
        self._depends = {}
        self._content = []

        pattern = re.compile(r"<(.*?depend)>(.*?)</.*?depend>")
        lines = path.read_text().split("\n")
        for line in lines:
            match = pattern.search(line)
            if not match:
                self._content.append(line)
                continue
            tag = match.group(1)
            pkg = match.group(2)
            if tag not in self._depends:
                pkgs = set()
                self._depends[tag] = pkgs
                self._content.append((tag, pkgs))
            self._depends[tag].add(pkg)

    def write(self):
        lines = []
        for line in self._content:
            if type(line) is str:
                lines.append(line)
            else:
                tag, pkgs = line
                for pkg in sorted(pkgs):
                    lines.append(f"  <{tag}>{pkg}</{tag}>")
        self._path.write_text("\n".join(lines))

    def add_depend(self, tag: str, pkgs: str | list[str]):
        pkgs = [pkgs] if pkgs is str else pkgs
        for pkg in pkgs:
            self._depends[tag].add(pkg)
