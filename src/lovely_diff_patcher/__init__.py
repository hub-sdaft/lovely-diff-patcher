from diff_match_patch import diff_match_patch as DMP
from pathlib import Path
from .patcher import __find_patches, __panic, __info, __apply_patch, __create_toml_file
from re import sub

import argparse

__version__ = "0.2.2"
__author__ = "hub-sdaft"

def patch_file(source_path: Path, patched_path: Path, output_path: Path,
         priority: int, dump_lua: bool, manifest_version: str):
    
    with open(source_path, "r") as f:
        source_content = str(f.read())

    with open(patched_path, "r") as f:
        patched_content = str(f.read())
    
    # Find the patches
    try:
        patches = __find_patches(source_content, patched_content)
    except Exception as e:
        __panic(e)

    len_patches = len(patches)
    __info(f"Found {len_patches} patch{'' if len_patches == 1 else 'es'}")

    # Create output
    output = __create_toml_file(patches, source_path, manifest_version, dump_lua, priority)
    
    with open(output_path, "w") as f:
        f.write(output)

    __info(f"Patch file written successfully at {output_path}")


def cli_main():
    argparser = argparse.ArgumentParser(
        prog = "lovely-diff-patcher",
        description = "Creates a TOML patch file to be used with the Lovely Injector"
    )

    argparser.register('type', 'path', lambda s: Path(s))

    argparser.add_argument(
        "source", type="path",
        help="The path to the un-patched source file"
    )
    argparser.add_argument(
        "patched", type="path",
        help="The path to the already patched file"
    )
    argparser.add_argument(
        "output", type="path",
        nargs="?", default="lovely.toml",
        help="The path to the output TOML patch file. Defaults to 'lovely.toml'."
    )

    argparser.add_argument(
        "-p", "--priority", type=int,
        nargs="?", default=0,
        help="The priority value to specify in the output file's manifest metadata. Defaults to 0."
    )
    argparser.add_argument(
        "-d", "--dump-lua", action="store_true",
        help="Whether to set the dump_lua flag in the output file's manifest metadata"
    )
    argparser.add_argument(
        "-v", "--manifest-version", type=str,
        nargs="?", default="1.0.0",
        help="The version to specify in the output file's manifest metadata. Defaults to 1.0.0."
    )

    argparser.add_argument(
        "--version", action="version",
        version=f"%(prog)s {__version__} by {__author__}"
    )

    args = argparser.parse_args()
    
    source_path = Path.resolve(args.source)
    if not Path.exists(source_path):
        __panic(f"Source path '{args.source}' does not exist")
    
    patched_path = Path.resolve(args.patched)
    if not Path.exists(patched_path):
        __panic(f"Patched path '{args.patched}' does not exist")

    patch_file(
        source_path=args.source.as_posix(),
        patched_path=args.patched.as_posix(),
        output_path=args.output.as_posix(),
        priority=args.priority,
        dump_lua=args.dump_lua,
        manifest_version=args.manifest_version
    )
