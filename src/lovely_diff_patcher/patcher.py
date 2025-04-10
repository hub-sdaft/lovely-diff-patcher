from diff_match_patch import diff_match_patch as DMP

import re

__DIFF_DELETE = -1
__DIFF_INSERT = 1
__DIFF_EQUAL = 0

def __panic(message):
    print(f"[ERROR] {message}")
    exit(1)

def __info(message):
    print(f"[INFO] {message}")


def __line_diff(source, patched):
    dmp = DMP()
    a = dmp.diff_linesToChars(source, patched)
    diffs = dmp.diff_main(a[0], a[1], False)
    dmp.diff_charsToLines(diffs, a[2])
    return diffs

def __is_text_unique(text: str, source: str) -> bool:
    matches = 0
    for _ in re.finditer(re.escape(text), source):
        matches += 1
        if matches > 1:
            break
    
    if matches == 0:
        raise ValueError(f"Line not present in source:\n{text}'")
    
    return (matches == 1)

def __apply_patch(patch: dict[str, str], source: str) -> str:
    pos = patch.get("position")
    pattern = patch.get("pattern")
    payload = patch.get("payload")

    if not __is_text_unique(pattern, source):
        raise ValueError(f"Cannot apply patch with non-unique pattern:\n'{pattern}'")

    if pos == 'at':
        return re.sub(re.escape(pattern), payload, source)
    
    elif pos == 'before':
        return re.sub(re.escape(pattern), payload + pattern, source)
    
    elif pos == 'after':
        return re.sub(re.escape(pattern), pattern + payload, source)
    
    else:
        raise ValueError(f"Invalid position '{pos}'")

def __find_patches(src, patched):
    i = 0
    diff_blocks = __line_diff(src, patched)
    patches: list[dict] = [] 

    while i < len(diff_blocks):
        diff_action, diff_text = diff_blocks[i]
        diff_text = diff_text.strip()

        if diff_text == "":
            i += 1
            continue

        def find_unique_pattern(search_range):
            for j in search_range:
                other_diff_action, other_diff_text = diff_blocks[j]
            
                if other_diff_action != __DIFF_EQUAL:
                    continue
                
                lines = other_diff_text.split("\n")
                current_target = ""

                for line in lines:
                    current_target += line + "\n"
                    if __is_text_unique(current_target, src):
                        return current_target
                
                return None

        # EQUAL ##########################################
        if diff_action == __DIFF_EQUAL:
            pass

        # DELETE ###########################################
        elif diff_action == __DIFF_DELETE:
            is_diff_unique = __is_text_unique(diff_text, src)
            
            if i + 1 < len(diff_blocks) and diff_blocks[i+1][0] == __DIFF_INSERT:
                new_text = diff_blocks[i+1][1] #.strip()

                if is_diff_unique:
                    patch = {
                        "pattern": diff_text,
                        "payload": new_text,
                        "position": "at",
                    }

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
                            f"'{diff_text}'\n"
                            "to:\n"
                            f"'{new_text}'"
                        )
                    
                    patch = {
                        "pattern": diff_text,
                        "payload": replace_with,
                        "position": "at"
                    }

                i += 1

            else:
                if is_diff_unique:
                    patch = {
                        "pattern": diff_text,
                        "payload": "",
                        "position": "at"
                    }
                else:
                    raise ValueError(
                        "Cannot determine which line to delete, containing:\n"
                        f"'{diff_text}'"
                    )

            patches.append(patch)
            src = __apply_patch(patch, src)

        # INSERT ######################################################################
        # Insert directly: find a unique pattern as reference
        elif diff_action == __DIFF_INSERT:
            # Find unique target in blocks before
            unique_pattern = find_unique_pattern(range(i-1, 0, -1))
            position = "after"

            # Find uinque target in the blocks after
            if unique_pattern is None:
                unique_pattern = find_unique_pattern(range(i+1, len(diff_blocks)))
                position = "before"

            if unique_pattern is None:
                raise ValueError(f"Cannot find a target for insertion of text:\n'{diff_text}'")
            
            patch = {
                "pattern": unique_pattern,
                "payload": diff_text,
                "position": position
            }
            patches.append(patch)
            src = __apply_patch(patch, src)
            
        i += 1

    return patches

def __create_toml_file(patches, target, version, dump_lua, priority, compact = False):
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
match_indent = true
times = 1

"""
    return toml