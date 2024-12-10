import pathlib
import xml.etree.ElementTree as etree


class RosPackageXml:
    def __init__(self, path: pathlib.Path):
        self.tree = etree.parse(path)
        self.root = self.tree.getroot()

    def get_name(self, include_prefix=True):
        name = self.root.find("name").text
        return name if include_prefix else name.removeprefix("autoware_")

    def list_package_depends(self):
        pkgs = set()
        for node in self.root:
            if node.tag.endswith("depend") or node.tag == "name":
                pkgs.add(node.text)
        return pkgs
