from diff_match_patch import diff_match_patch

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
#     print(patch)