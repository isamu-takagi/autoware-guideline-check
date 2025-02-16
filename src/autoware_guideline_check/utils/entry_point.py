import argparse
import pathlib


class EntryPoint:
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument("files", nargs="*")

    def main(self, func, argv=None):
        args = self.parser.parse_args(argv)
        code = 0
        for file in args.files:
            path = pathlib.Path(file)
            code = code & func(path, args)
        return code
