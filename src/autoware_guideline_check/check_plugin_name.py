import argparse
import pathlib
import xml.etree.ElementTree as etree


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("filenames", nargs="*")
    args = parser.parse_args(argv)

    result = 0
    for filename in args.filenames:
        filepath = pathlib.Path(filename)
        print(filepath)

    return result
