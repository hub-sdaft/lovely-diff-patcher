from diff_match_patch import diff_match_patch as DMP
from enum import Enum, auto
from pathlib import Path
from pprint import pprint

import argparse
import re

__version__ = "0.0.1"

DIFF_DELETE = -1
DIFF_INSERT = 1
DIFF_EQUAL = 0


def panic(message):
    print(f"[ERROR] {message}")
    exit(1)

def info(message):
    print(f"[INFO] {message}")


def line_diff(source, patched):
    dmp = DMP()
    a = dmp.diff_linesToChars(source, patched)
    diffs = dmp.diff_main(a[0], a[1], False)
    dmp.diff_charsToLines(diffs, a[2])
    return diffs

def is_text_unique(text: str, source: str) -> bool:
    matches = 0
    for _ in re.finditer(re.escape(text), source):
        matches += 1
        if matches > 1:
            break
    
    if matches == 0:
        raise ValueError(f"Line {text} is not present in source")
    
    return (matches == 1)

def apply_patch(patch: dict[str, str], source: str) -> str:
    pos = patch.get("position")
    pattern = patch.get("pattern")
    payload = patch.get("payload")

    if not is_text_unique(pattern, source):
        raise ValueError("Cannot apply patch with non-unique pattern")

    if pos == 'at':
        return re.sub(re.escape(pattern), payload, source)
    
    elif pos == 'before':
        return re.sub(re.escape(pattern), payload + pattern, source)
    
    elif pos == 'after':
        return re.sub(re.escape(pattern), pattern + payload, source)
    
    else:
        raise ValueError(f"Invalid position '{pos}'")

def find_patches(src, patched):
    i = 0
    diff_blocks = line_diff(src, patched)
    patches: list[dict] = [] 

    while i < len(diff_blocks):
        diff_action, diff_text = diff_blocks[i]

        def find_unique_pattern(search_range):
            for j in search_range:
                other_diff_action, other_diff_text = diff_blocks[j]
            
                if other_diff_action != DIFF_EQUAL:
                    continue
                
                lines = other_diff_text.split("\n")
                current_target = ""

                for line in lines:
                    current_target += line
                    if is_text_unique(current_target, src):
                        return current_target
                
                return None

        # EQUAL ##########################################
        if diff_action == DIFF_EQUAL:
            pass

        # DELETE ###########################################
        elif diff_action == DIFF_DELETE:
            is_diff_unique = is_text_unique(diff_text, src)
            
            if i + 1 < len(diff_blocks) and diff_blocks[i+1][0] == DIFF_INSERT:
                new_text = diff_blocks[i+1][1]

                if is_diff_unique:
                    patch = {
                        "pattern": diff_text,
                        "payload": new_text,
                        "position": "at",
                    }
                    patches.append(patch)
                    src = apply_patch(patch, src)

                # Pattern is not unique!
                else:
                    replace_with = ""
                    # find a broader match: this is more difficult
                    # Find match in blocks before
                    unique_pattern = find_unique_pattern(range(i-1, 0, -1))
                    replace_with = unique_pattern + new_text

                    # Find match in blocks after
                    if unique_pattern is None:
                        unique_pattern = find_unique_pattern(range(i+1, len(diff_blocks)))
                        replace_with = diff_blocks[i+1][1] + new_text

                    if unique_pattern is None:
                        raise ValueError(
                            f"Cannot find target for substitution from:\n"
                            f"{diff_text}\n"
                            "to:\n"
                            f"{new_text}"
                        )
                    
                    patch = {
                        "pattern": diff_text,
                        "payload": replace_with,
                        "position": "at"
                    }
                    patches.append(patch)
                    src = apply_patch(patch, src)

                i += 1

            else:
                if is_diff_unique:
                    patch = {
                        "pattern": diff_text,
                        "payload": "",
                        "position": "at"
                    }
                    patches.append(patch)
                    src = apply_patch(patch, src)
                else:
                    raise ValueError("Cannot determine which line to delete. You tried to delete this text: ...")

        # INSERT ######################################################################
        # Insert directly: find a unique pattern as reference
        elif diff_action == DIFF_INSERT:
            # Find unique target in blocks before
            unique_pattern = find_unique_pattern(range(i-1, 0, -1))
            position = "after"

            # Find uinque target in the blocks after
            if unique_pattern is None:
                unique_pattern = find_unique_pattern(range(i+1, len(diff_blocks)))
                position = "before"

            if unique_pattern is None:
                raise ValueError("Cannot find a target for this insert.")
            
            patch = {
                "pattern": unique_pattern,
                "payload": diff_text,
                "position": position
            }
            patches.append(patch)
            src = apply_patch(patch, src)
            
        i += 1

    return patches

def create_toml_file(patches, target, version, dump_lua, priority, compact = False):
    toml = f'''# Generated with lovely-diff-patcher
[manifest]
version = "{version}"
dump_lua = {"true" if dump_lua == True else "false"}
priority = {priority}

'''
    
    for patch in patches:
        toml += f"""[[patches]]
[patches.pattern]
target = "{target}"
pattern = '''
{patch.get("pattern")}'''
payload = '''
{patch.get("payload")}'''
position = "{patch.get("position")}"
match_indent = false
times = 1

"""
    return toml

def main(source_path: Path, patched_path: Path, output_path: Path,
         priority: int, dump_lua: bool, manifest_version: str):
    
    with open(source_path, "r") as f:
        source_content = str(f.read())

    with open(patched_path, "r") as f:
        patched_content = str(f.read())
    
    # Find the patches
    try:
        patches = find_patches(source_content, patched_content)
    except Exception as e:
        panic(e)

    len_patches = len(patches)
    info(f"Found {len_patches} patch{'' if len_patches == 1 else 'es'}")

    # Cross check
    repatched = source_content
    for patch in patches:
        repatched = apply_patch(patch, repatched)
    if repatched == patched_content:
        info(f"Cross check passed")

    # Create output
    output = create_toml_file(patches, source_path, manifest_version, dump_lua, priority)
    
    with open(output_path, "w") as f:
        f.write(output)

    info(f"Patch file written successfully at {output_path}")


if __name__ == "__main__":
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
        version=f"%(prog)s {__version__}"
    )

    args = argparser.parse_args()
    
    source_path = Path.resolve(args.source)
    if not Path.exists(source_path):
        panic(f"Source path '{args.source}' does not exist")
    
    patched_path = Path.resolve(args.patched)
    if not Path.exists(patched_path):
        panic(f"Patched path '{args.patched}' does not exist")

    main(
        source_path=args.source.as_posix(),
        patched_path=args.patched.as_posix(),
        output_path=args.output.as_posix(),
        priority=args.priority,
        dump_lua=args.dump_lua,
        manifest_version=args.manifest_version
    )
