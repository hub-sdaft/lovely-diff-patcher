# lovely-diff-patcher
Python utility for patching files with Lovely Injector

## Usage
Use `-h` to get help.

    usage: lovely-diff-patcher [-h] [-p [PRIORITY]] [-d] [-v [MANIFEST_VERSION]] [--version] source patched output

    Creates a TOML patch file to be used with the Lovely Injector

    positional arguments:
    source                The path to the un-patched source file
    patched               The path to the already patched file
    output                The path to the output TOML patch file

    options:
    -h, --help            show this help message and exit
    -p [PRIORITY], --priority [PRIORITY]
                            The priority value to specify in the output file's manifest metadata. Defaults to 0.
    -d, --dump-lua        Whether to set the dump_lua flag in the output file's manifest metadata
    -v [MANIFEST_VERSION], --manifest-version [MANIFEST_VERSION]
                            The version to specify in the output file's manifest metadata. Defaults to 1.0.0.
    --version             show program's version number and exit