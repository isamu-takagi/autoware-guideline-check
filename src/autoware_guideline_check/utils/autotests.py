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

from .testsuite import TestCase, TestSuite
from .workspace import Package


def generate_autotests(package: Package):
    schema_dir = package.path.joinpath("schema")
    config_dir = package.path.joinpath("config")
    cases = []
    for schema in schema_dir.glob("**/*.schema.json"):
        base = schema.name.removesuffix(".schema.json")
        for config in config_dir.glob(f"**/{base}*.param.yaml"):
            data = {
                "schema": {"file": schema},
                "params": {"file": config},
            }
            cases.append(TestCase(data))
    return TestSuite(cases)
