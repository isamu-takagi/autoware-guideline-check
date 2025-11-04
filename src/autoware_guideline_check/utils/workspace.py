# Copyright 2025 The Autoware Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from pathlib import Path
from xml.etree import ElementTree

from ..common.spec import SpecFile


class Package:
    def __init__(self, path: Path, configs: list):
        root = ElementTree.parse(path / "package.xml")
        self._path = path
        self._name = root.find("name").text
        self._configs = configs

        self._files = []
        for export in root.findall("export"):
            for file in export.findall("autoware_guideline_check"):
                self._files.append(file.get("file"))
                self._configs.append(SpecFile(path / file.get("file")))

    @property
    def path(self):
        return self._path

    @property
    def name(self):
        return self._name

    @property
    def configs(self):
        return self._configs

    @property
    def files(self):
        return [self._path / file for file in self._files]


class Workspace:
    colcon_ignore = "COLCON_IGNORE"
    common_config = ".autoware-guideline-check.yaml"
    package_xml = "package.xml"

    def __init__(self, modules, paths: list[str]):
        self._packages = self.__init_packages(modules, paths)

    def get_package_share_directory(self, name: str):
        package = self._packages.get(name)
        if package:
            return package.path
        raise RuntimeError(f"Package {name} not found")

    @property
    def packages(self):
        return self._packages.values()

    @classmethod
    def __init_packages(cls, modules, paths: list[str]):
        packages = []
        for path in paths:
            packages.extend(cls.__list_packages(modules, Path(path), []))
        return {package.name: package for package in packages}

    @classmethod
    def __list_packages(cls, modules, base: Path, configs: list):
        if base.joinpath(cls.colcon_ignore).exists():
            return []
        if base.joinpath(cls.common_config).exists():
            configs = configs.copy()
            configs.append(modules.parse_config(base.joinpath(cls.common_config)))
        if base.joinpath(cls.package_xml).exists():
            return [Package(base, configs.copy())]
        packages = []
        for path in base.iterdir():
            if path.is_dir():
                packages.extend(cls.__list_packages(modules, path, configs))
        return packages
