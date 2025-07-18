import sys
import launch
from launch import LaunchDescription
from launch import LaunchIntrospector
from launch import LaunchService

from collections import deque
from typing import Text, Dict, Any
from launch import Substitution
from launch import Event

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

def show(ld: LaunchDescription):
  print("====================")
  print(LaunchIntrospector().format_launch_description(ld))
  print("====================")

def exec(argv, ld: LaunchDescription):
  ls = LaunchService(argv=argv)
  ls.include_launch_description(ld)
  return ls.run()

def aaaa(ld: LaunchDescription):
  context = DummyContext()
  entities = deque([ld])
  while entities:
    entity = entities.popleft()
    print(entity)
    result = entity.visit(context)
    entities.extend(result if result else [])

def main(argv=None):
  launch_file_path = "test.launch.xml"
  ld = launch.LaunchDescription([
    launch.actions.IncludeLaunchDescription(
      launch.launch_description_sources.AnyLaunchDescriptionSource(
          launch_file_path
      ),
      #launch_arguments=parsed_launch_arguments,
    ),
  ])

  # show(ld)
  # exec(argv, ld)
  aaaa(ld)
  return 0

if __name__ == '__main__':
    sys.exit(main())
