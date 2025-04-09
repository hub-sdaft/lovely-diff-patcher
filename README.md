# lovely-diff-patcher
Python utility for patching files with Lovely Injector.

Given a source file and a patched file, it creates the TOML file that patches
the source in the patched exactly, if possible.

## Requirements
* Python >= 3.10
* `pip`

## Installation

You can install the package with `pip`
    
    pip install git+https://github.com/hub-sdaft/lovely-diff-patcher

> **NOTE**: The command `lovely-diff-patcher` will be added to the system's current path

## Usage
Usage:

    lovely-diff-patcher [-h] [-p [PRIORITY]] [-d] [-v [MANIFEST_VERSION]] [--version] source patched [output]

> Use `-h` to get help and see this exact message

### Positional Arguments
* `source`: The path to the un-patched source file
* `patched`: The path to the already patched file
* `output`: The path to the output TOML patch file

### Options
* `-h`: show the help message
* `-p [PRIORITY], --priority [PRIORITY]`: The priority value to specify in the output file's manifest metadata. Defaults to 0.
* `-d, --dump-lua`: Whether to set the dump_lua flag in the output file's manifest metadata
* `-v [MANIFEST_VERSION], --manifest-version [MANIFEST_VERSION]`: The version to specify in the output file's manifest metadata. Defaults to 1.0.0.
* `--version`: show program's version number and exit

## Credits
* hub-sdaft
* Lovely Injector repository: [ethangree-dev/lovely-injector](https://github.com/ethangreen-dev/lovely-injector)
* [dmsnell/diff-match-patch](https://github.com/dmsnell/diff-match-patch/), originally by Neil Fraser