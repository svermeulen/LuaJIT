
import sys
import os
from pathlib import Path
import subprocess
import logging
import shutil
import platform

cwd = Path.cwd()
script_dir = cwd.joinpath(Path(__file__).parent)

# uncomment for extra debugging
# log_path = Path.cwd().joinpath(f"build_luajit_{random.randint(1, 99999999999999)}.log")
# if log_path.exists():
#     log_path.unlink()
# logging.basicConfig(filename=log_path, level=logging.DEBUG)

out_dir = cwd.joinpath(sys.argv[1]).resolve()

logging.debug(f"Running luajit build script with args:\ncwd: {cwd}\nluajit_source: {script_dir}\nout_dir: {out_dir}")

out_dir.mkdir(parents=False, exist_ok=False)

if platform.system() == 'Linux':
    args = ['make', '-j{}'.format(os.cpu_count()), 'V=1', 'PREFIX={}'.format(out_dir), 'install']
    logging.debug(f"Running make: {args}")
    subprocess.run(args, cwd=script_dir, check=True)

    lib_path_1 = out_dir.joinpath("lib/libluajit-5.1.so")
    actual_lib_path = lib_path_1.resolve()

    lib_path_1.unlink()
    shutil.copy2(actual_lib_path, lib_path_1)

    exe_path_1 = out_dir.joinpath("bin/luajit")
    actual_exe_path = exe_path_1.resolve()

    exe_path_1.unlink()
    shutil.copy2(actual_exe_path, exe_path_1)
    actual_exe_path.unlink()

elif platform.system() == 'Windows':
    src_dir = script_dir.joinpath("src")
    developer_command_prompt_bat = os.getenv("VS_DEVELOPER_COMMAND_PROMPT")
    assert developer_command_prompt_bat is not None, "Unable to locate visual studio developer command prompt.  Expected to find it from env. var 'VS_DEVELOPER_COMMAND_PROMPT'"
    subprocess.run(f'"{developer_command_prompt_bat}" && msvcbuild.bat', cwd=src_dir, check=True, shell=True)

    out_bin_dir = out_dir.joinpath("bin")
    out_bin_dir.mkdir(parents=False, exist_ok=False)
    shutil.copy(src_dir.joinpath("lua51.dll"), out_bin_dir)
    shutil.copy(src_dir.joinpath("luajit.exe"), out_bin_dir)

    out_lib_dir = out_dir.joinpath("lib")
    out_lib_dir.mkdir(parents=False, exist_ok=False)

    shutil.copy(src_dir.joinpath("lua51.lib"), out_lib_dir)

    out_include_dir = out_dir.joinpath("include/luajit-2.1")
    out_include_dir.mkdir(parents=True, exist_ok=True)

    for header in ["lauxlib.h", "luaconf.h", "lua.h", "lua.hpp", "luajit.h", "lualib.h"]:
      shutil.copy(src_dir.joinpath(header), out_include_dir)

logging.debug(f"Luajit built successfully")

