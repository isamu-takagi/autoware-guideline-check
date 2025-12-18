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

import json

import jsonschema
import yaml

from .types.filepath import FilePath
from .utils.testsuite import TestResult, TestStatus


class TestInstance:
    def __init__(self, schema, params):
        self.result = TestResult.Null()
        self.schema = schema
        self.params = params

    def execute(self):
        self.result = self.validate()

    def validate(self):
        with self.schema.open() as fp:
            schema = json.load(fp)
        with self.params.open() as fp:
            target = yaml.safe_load(fp)
        try:
            absolute = self.schema.absolute()
            resolver = jsonschema.RefResolver(f"file://{absolute}", schema)
            jsonschema.validate(target, schema, resolver=resolver)
            return TestResult.Success("OK", "")
        except jsonschema.ValidationError as error:
            return TestResult.Failure(error.message, "")
        except Exception as error:
            return TestResult.Error(repr(error), "")


class TestTemplate:
    def execute(self, package, workspace):
        raise NotImplementedError()


class UserTestTemplate(TestTemplate):
    def __init__(self, definition):
        pass


class AutoTestTemplate(TestTemplate):
    def __init__(self, definition):
        pass

    def execute(self, package, workspace):
        for schema in package.path.glob("schema/**/*.schema.json"):
            prefix = schema.name.removesuffix(".schema.json")
            for config in package.path.glob(f"config/**/{prefix}*.param.yaml"):
                yield TestInstance(schema, config)


class ParameterSchemaValidation:
    def __init__(self):
        self.cache = {}

    @property
    def name(self):
        return "parameter-schema-validation"

    def execute(self, package, workspace):
        templates = self.parse(package)
        testcases = self.apply(package, workspace, templates)
        return testcases

    def apply(self, package, workspace, templates):
        testcases = []
        for template in templates:
            testcases.extend(template.execute(package, workspace))
        return testcases

    def parse(self, package):
        templates = []
        for config in package.share_configs:
            templates.extend(self.__parse_share_config(config))
        for config in package.local_configs:
            templates.extend(self.__parse_local_config(config))
        return templates

    def __parse_share_config(self, config):
        if config not in self.cache:
            self.cache[config] = self.__parse_local_config(config)
        return self.cache[config]

    def __parse_local_config(self, config):
        data = config.data.pop(self.name, None)
        data = [] if data is None else data
        if type(data) is not list:
            raise TypeError(f"{self.name} must be a list ({config.path})")
        templates = []
        for definition in data:
            test_type = definition.pop("type", "custom")
            if test_type == "custom":
                templates.append(UserTestTemplate(definition))
            elif test_type == "auto":
                templates.append(AutoTestTemplate(definition))
            else:
                print(f"Invalid type: {test_type} ({config.path})")
                # raise ValueError(f"Invalid type: {test_type} ({config.path})")
        return templates


def check(data: dict, workspace):
    try:
        schema = FilePath.Parse(data["schema"], workspace)
        params = FilePath.Parse(data["params"], workspace)
        return validate(schema, params)
    except Exception as error:
        return TestResult.Error(repr(error), "")
