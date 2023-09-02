
import argparse
from dataclasses import dataclass
from pathlib import Path
import logging
import os
import subprocess
import sys
import platform
from typing import Optional, Tuple, List, cast
import random

@dataclass
class CommandLineArgs:
    script: Path
    shared_lib: Path
    executable: Path
    linktreedir: Optional[Path]
    use_linktree_dir_as_cwd: bool

def _parse_args() -> Tuple[CommandLineArgs, List[str]]:
    parser = argparse.ArgumentParser(description='run_luajit')

    parser.add_argument(
        '--shared-lib',
        type=str)

    parser.add_argument(
        '--executable',
        type=str)

    parser.add_argument(
        '--linktreedir',
        type=str)

    parser.add_argument(
        'script',
        type=str)

    parser.add_argument(
        "--use-linktree-dir-as-cwd",
        action="store_true",
    )

    arg_divide_index = sys.argv.index('--')
    assert arg_divide_index != -1, "Expected to find '--' in command line args"

    args_before_double_dash = sys.argv[1:arg_divide_index]
    args_after_double_dash = sys.argv[arg_divide_index + 1:]

    raw_args = parser.parse_args(args_before_double_dash)

    shared_lib = Path(raw_args.shared_lib)
    executable = Path(raw_args.executable)
    script = Path(raw_args.script)
    linktreedir = Path(raw_args.linktreedir) if raw_args.linktreedir is not None else None

    start_dir = Path.cwd()

    if not shared_lib.is_absolute():
        shared_lib = start_dir.joinpath(shared_lib)

    if not executable.is_absolute():
        executable = start_dir.joinpath(executable)

    if not script.is_absolute():
        script = start_dir.joinpath(script)

    if linktreedir is not None and not linktreedir.is_absolute():
        linktreedir = start_dir.joinpath(linktreedir)

    assert shared_lib.exists()
    assert executable.exists()
    assert script.exists()
    assert linktreedir is None or linktreedir.exists()

    return CommandLineArgs(
        script=script,
        shared_lib=shared_lib,
        use_linktree_dir_as_cwd=raw_args.use_linktree_dir_as_cwd,
        linktreedir=linktreedir,
        executable=executable), args_after_double_dash

def _main_impl():
    args, script_args = _parse_args()

    logging.debug(f"Received command line args: {repr(args)}")

    platform_name = platform.system()
    is_windows = platform_name == 'Windows'

    if not is_windows:
        assert platform_name == 'Linux', f"Untested platform '{platform_name}'"

    if is_windows:
        # The luajit dll is not in the same directory as the executable so we need
        # to add that directory to the path
        current_path = os.environ["PATH"]
        assert len(current_path) > 0
        os.environ["PATH"] = str(args.shared_lib.parent) + ";" + current_path
    else:
        new_lib_path = str(args.shared_lib.parent)

        if args.linktreedir is not None:
            new_lib_path += ":" + str(args.linktreedir)

        lib_path = os.environ.get("LD_LIBRARY_PATH", None)

        if lib_path is None:
            lib_path = new_lib_path
        else:
            lib_path = new_lib_path + ":" + lib_path

        os.environ["LD_LIBRARY_PATH"] = lib_path

    lua_path:str

    if args.linktreedir is None:
        lua_path = ""
    else:
        lua_path = str(args.linktreedir) + "/?.lua;" + str(args.linktreedir) + "/?/init.lua"

    os.environ['LUA_PATH'] = lua_path

    extension = ".dll" if is_windows else ".so"

    lua_cpath:str

    if args.linktreedir is None:
        lua_cpath = ""
    else:
        lua_cpath = str(args.linktreedir) + "/?" + extension

    os.environ['LUA_CPATH'] = lua_cpath

    luajit_args = [str(args.executable), str(args.script)] + script_args

    logging.debug(f"Running luajit with args: '{luajit_args}'")

    cwd = None

    if args.use_linktree_dir_as_cwd:
        assert args.linktreedir is not None
        cwd = args.linktreedir

    result = subprocess.run(luajit_args, cwd=cwd)

    if result.returncode == 0:
        logging.debug(f"Luajit completed successfully")
    else:
        logging.debug(f"Lua script or luajit failed")
        exit(result.returncode)

def main():
    # Uncomment for debugging
    # log_path = Path.cwd().joinpath(f"run_luajit_{random.randint(1, 99999999999999)}.log")
    # if log_path.exists():
    #     log_path.unlink()
    # logging.basicConfig(filename=log_path, level=logging.DEBUG)

    try:
        _main_impl()
    except Exception as e:
        logging.error("Failure with run_luajit.py: " + str(e))
        raise 

main()

