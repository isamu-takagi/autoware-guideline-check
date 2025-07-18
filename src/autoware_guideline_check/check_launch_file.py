import pathlib
import collections
from typing import Text, Dict, Any

from launch import Event
from launch import LaunchDescription
from launch import Substitution
from launch.actions import IncludeLaunchDescription


class DummyContext:
  def __init__(self):
    self.launch_configurations = {}

  def perform_substitution(self, substitution: Substitution) -> Text:
    print(" - perform_substitution", substitution)
    return substitution.perform(self)

  def would_handle_event(self, event: Event) -> bool:
    print(" - would_handle_event", event)
    return False

  def extend_locals(self, extensions: Dict[Text, Any]) -> None:
    print(" - extend_locals", extensions)


def aaaa(ld: LaunchDescription):
  context = DummyContext()
  entities = collections.deque([ld])
  while entities:
    entity = entities.popleft()
    print(entity)
    result = entity.visit(context)
    entities.extend(result if result else [])


def process_file(path: pathlib.Path, args):
    ld = LaunchDescription([IncludeLaunchDescription(path)])
    aaaa(ld)
    return 0

def main(argv=None):
    from .utils import EntryPoint
    return EntryPoint().main(process_file, argv)

if __name__ == "__main__":
    process_file("test.launch.xml", {})
