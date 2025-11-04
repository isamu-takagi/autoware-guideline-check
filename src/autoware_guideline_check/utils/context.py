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

import yaml


class ConfigFile:
    def __init__(self, path, templates):
        self._path = path
        self._templates = templates

    @property
    def path(self):
        return self._path


class Modules:
    def __init__(self):
        self._modules = []


class Context:
    def __init__(self):
        self._modules = []

    def create_config(self, path: Path):
        with path.open() as fp:
            config = yaml.safe_load(fp)
        templates = {}
        for module in self._modules:
            templates[module.name] = module.parse(config)
        return templates
