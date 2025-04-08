from diff_match_patch import diff_match_patch
from pprint import pprint

DMP = diff_match_patch()
DMP.Match_Threshold = 0.0
DMP.Patch_DeleteThreshold = 0.0

src_file = "./tests/source.py"
patched_file = "./tests/patched.py"

with open(src_file, "r") as f:
    src = str(f.read())

with open(patched_file, "r") as f:
    patched = str(f.read())


patches = DMP.patch_make(src, patched)

print(len(patches), "patches")

# for patch in patches:
#     print(patch.start1, patch.start2, patch.length1, patch.length2)

def line_diff(source, patched):
    dmp = diff_match_patch()
    a = dmp.diff_linesToChars(source, patched)
    diffs = dmp.diff_main(a[0], a[1], False)
    dmp.diff_charsToLines(diffs, a[2])
    return diffs

pprint(line_diff(src, patched))
