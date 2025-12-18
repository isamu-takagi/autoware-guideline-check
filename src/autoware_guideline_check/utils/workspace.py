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

import yaml


class Config:
    def __init__(self, path: Path):
        data = yaml.safe_load(path.read_text())
        self._path = path
        self._data = data if data else {}

    @property
    def path(self):
        return self._path

    @property
    def data(self):
        return self._data


class Package:
    def __init__(self, path: Path, configs: list):
        root = ElementTree.parse(path / "package.xml")
        self._path = path
        self._name = root.find("name").text
        self._share_configs = configs
        self._local_configs = self.__list_package_configs(path, root)

    @staticmethod
    def __list_package_configs(path, root):
        configs = []
        for export in root.findall("export"):
            for tag in export.findall("autoware_guideline_check"):
                configs.append(Config(path / tag.get("file")))
        return configs

    @property
    def path(self):
        return self._path

    @property
    def name(self):
        return self._name

    @property
    def share_configs(self):
        return self._share_configs

    @property
    def local_configs(self):
        return self._local_configs


class Workspace:
    colcon_ignore = "COLCON_IGNORE"
    common_config = ".autoware-guideline-check.yaml"
    package_xml = "package.xml"

    def __init__(self, paths: list[str]):
        self._packages = self.__init_packages(paths)

    def get_package_share_directory(self, name: str):
        package = self._packages.get(name)
        if package:
            return package.path
        raise RuntimeError(f"Package {name} not found")

    @property
    def packages(self):
        return self._packages.values()

    @classmethod
    def __init_packages(cls, paths: list[str]):
        packages = []
        for path in paths:
            packages.extend(cls.__list_packages(Path(path), []))
        return {package.name: package for package in packages}

    @classmethod
    def __list_packages(cls, base: Path, configs: list):
        if base.joinpath(cls.colcon_ignore).exists():
            return []
        if base.joinpath(cls.common_config).exists():
            configs = [*configs, Config(base.joinpath(cls.common_config))]
        if base.joinpath(cls.package_xml).exists():
            return [Package(base, configs.copy())]
        packages = []
        for path in base.iterdir():
            if path.is_dir():
                packages.extend(cls.__list_packages(path, configs))
        return packages
