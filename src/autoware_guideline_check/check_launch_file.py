import collections
import pathlib
from typing import Any, Dict, Text

from launch import Event, Substitution
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, SetLaunchConfiguration
from launch.launch_context import LaunchContext
from launch.substitutions import LaunchConfiguration, TextSubstitution


class DummyDict(collections.abc.MutableMapping):
    def __init__(self):
        self.data = {}
        self.used = collections.defaultdict(int)

    def __iter__(self):
        return iter(self.data)

    def __len__(self):
        return len(self.data)

    def __contains__(self, item):
        return item in self.data

    def __getitem__(self, item):
        self.used[item] += 1
        return self.data[item]

    def __setitem__(self, item, value):
        self.data[item] = value

    def __delitem__(self, item):
        del self.data[item]


class DummyContext:
    def __init__(self):
        self.__context = LaunchContext()
        self.launch_configurations = DummyDict()

    @property
    def is_shutdown(self):
        return True

    @property
    def environment(self):
        return self.__context.environment

    @property
    def locals(self):
        return self.__context.locals

    def perform_substitution(self, substitution: Substitution) -> Text:
        return substitution.perform(self)

    def would_handle_event(self, event: Event) -> bool:
        return False

    def extend_locals(self, extensions: Dict[Text, Any]) -> None:
        self.__context.extend_locals(extensions)

    def _push_environment(self):
        pass

    def _pop_environment(self):
        pass

    def _push_launch_configurations(self):
        pass

    def _pop_launch_configurations(self):
        pass


class DummyService:
    def __init__(self):
        self.entities = collections.deque()

    def include_launch_file(self, path):
        entities = IncludeLaunchDescription(str(path)).describe_sub_entities()
        for entity in entities:
            self.entities.extend(entity.describe_sub_entities())

    def run(self):
        context = DummyContext()
        while self.entities:
            entity = self.entities.popleft()
            if isinstance(entity, IncludeLaunchDescription):
                for name, value in entity.launch_arguments:
                    for substitution in name:
                        substitution.perform(context)
                    for substitution in value:
                        substitution.perform(context)
                continue
            if isinstance(entity, DeclareLaunchArgument):
                if entity.default_value is None:
                    context.launch_configurations[entity.name] = "NONE"
            result = entity.visit(context)
            self.entities.extend(result if result else [])

        data = context.launch_configurations.data
        used = context.launch_configurations.used
        for name in data:
            if used[name] == 0:
                print(name)


def process_file(path: pathlib.Path, args):
    service = DummyService()
    service.include_launch_file(path)
    service.run()
    return 0


def main(argv=None):
    from .utils import EntryPoint

    return EntryPoint().main(process_file, argv)


if __name__ == "__main__":
    process_file("test.launch.xml", {})
