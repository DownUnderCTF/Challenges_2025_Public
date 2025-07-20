import argparse
import base64
import zlib
import python_minifier


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("dll_path")
    parser.add_argument("script_path")
    parser.add_argument("output_path")
    args = parser.parse_args()

    print(f"Reading DLL: {args.dll_path}")
    with open(args.dll_path, "rb") as dll_file:
        dll_contents = dll_file.read()

    print(f"Reading script: {args.script_path}")
    with open(args.script_path, "r") as script_file:
        script_contents = script_file.read()

    dll_contents = base64.b64encode(zlib.compress(dll_contents, level=9)).decode()

    script_contents = f"DATA = '{dll_contents}'\n" + script_contents

    print("Minifying")
    script_contents = python_minifier.minify(
        script_contents,
        rename_locals=True,
        rename_globals=True,
        remove_asserts=True,
        preserve_globals=["DATA", "PASSWORD", "FLAG", "KEY"],
        remove_debug=True,
    )
    print(f"Writing: {args.output_path}")
    with open(args.output_path, "w") as output_file:
        output_file.write(script_contents)


if __name__ == "__main__":
    main()
