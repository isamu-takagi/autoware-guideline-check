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

from ..utils.workspace import Workspace


class FilePath:
    def __init__(self, path):
        self.path = path

    def __str__(self):
        return str(self.path)

    @staticmethod
    def Parse(data: dict, workspace: Workspace):
        if type(data) is not dict:
            raise TypeError(f"Expected type 'FilePath(dict)' but '{type(data).__name__}'")
        file = data.get("file")
        if file is None:
            raise KeyError("file")
        pkg = data.get("package")
        if pkg is None:
            return FilePath(Path(file))
        else:
            pkg = workspace.get_package_share_directory(pkg)
            return FilePath(Path(pkg) / Path(file))
