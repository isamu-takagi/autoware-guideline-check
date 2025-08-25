import collections
import pathlib
from typing import Any, Dict, Text

from ament_index_python.packages import PackageNotFoundError
from launch import Event, Substitution
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, SetLaunchConfiguration
from launch.launch_context import LaunchContext
from launch.substitutions import LaunchConfiguration, TextSubstitution
from launch.substitutions.substitution_failure import SubstitutionFailure
from launch_ros.substitutions import FindPackageShare

from launch import LaunchService
from launch.event_handlers.on_shutdown import OnShutdown
from launch.events import Shutdown

from launch.utilities import perform_substitutions

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

class DummyEventLoop:
    def run_in_executor(self, executor, func, *args):
        pass

class DummyContext:
    def __init__(self):
        self.__context = LaunchContext()
        self.launch_configurations = DummyDict()
        self.asyncio_loop = DummyEventLoop()
        self._event_handlers = []

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
        print("sub:", substitution.describe())
        if isinstance(substitution, FindPackageShare):
            result = perform_substitutions(self, substitution.package)
            result = "$(find-pkg-share " + result + ")"
            print("res:", result)
            return result
        result = substitution.perform(self)
        print("res:", result)
        return result

    def would_handle_event(self, event: Event) -> bool:
        return False

    def register_event_handler(self, handler, append=False) -> None:
        self._event_handlers.append(handler)

    def add_completion_future(self, future) -> None:
        pass

    def extend_locals(self, extensions: Dict[Text, Any]) -> None:
        self.__context.extend_locals(extensions)

    def extend_globals(self, extensions: Dict[Text, Any]) -> None:
        self.__context.extend_globals(extensions)

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
        try:
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
                        context.launch_configurations[entity.name] = "ARGS_NONE"
                result = entity.visit(context)
                self.entities.extend(result if result else [])
            data = context.launch_configurations.data
            used = context.launch_configurations.used
            for name in data:
                if used[name] == 0:
                    # print("unused:", name)
                    pass
        except PackageNotFoundError as error:
            print(error)
        except SubstitutionFailure as error:
            print(error)

        for handler in context._event_handlers:
            handler.handle(Shutdown(), context)



def process_file(path: pathlib.Path, args):
    print("======================")
    print(path)
    service = DummyService()
    service.include_launch_file(path)
    service.run()
    return 0


def main(argv=None):
    from .utils import EntryPoint

    return EntryPoint().main(process_file, argv)


if __name__ == "__main__":
    process_file("test.launch.xml", {})
