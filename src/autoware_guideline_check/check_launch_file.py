import collections
import pathlib
from typing import Any, Dict, Text

from launch import Event, Substitution
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_context import LaunchContext
from launch.substitutions import LaunchConfiguration, TextSubstitution


class DummyContext:
    def __init__(self):
        self.__context = LaunchContext()
        self.launch_configurations = {}

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
        if not isinstance(substitution, TextSubstitution):
            print(" - perform_substitution", substitution.describe())
        return substitution.perform(self)

    def would_handle_event(self, event: Event) -> bool:
        # print(" - would_handle_event", event)
        return False

    def extend_locals(self, extensions: Dict[Text, Any]) -> None:
        # print(" - extend_locals", extensions)
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
            print(entity)
            if isinstance(entity, IncludeLaunchDescription):
                print(" - Skip include launch description")
                continue
            if isinstance(entity, DeclareLaunchArgument):
                if entity.default_value is None:
                    context.launch_configurations[entity.name] = entity.default_value
            result = entity.visit(context)
            self.entities.extend(result if result else [])


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
