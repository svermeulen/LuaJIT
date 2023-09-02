
load("//bucktools/util:util.bzl", "select_file", "select_files")

native.export_file(
    name = "build_luajit.py",
    src = "build_luajit.py",
)

# It would be nice to avoid just assuming python3 here
# But it looks like prelude rules kinda do the same in prelude/toolchains/python.bzl
genrule(
    name = "build_luajit",
    cmd = "python3 build_luajit.py $OUT",
    srcs = glob(["**/*"]),
    out = "luajit",
)

select_files(
    name = "luajit-include-files",
    filter = "include/luajit-2.1/**/*",
    srcs = [":build_luajit"],
    strip_prefix = select({
        "DEFAULT": "include/luajit-2.1/",
        "config//os:windows": "include\\luajit-2.1\\",
    }),
    out = "lua",
)

select_file(
    name = "luajit-shared-lib",
    filter = select({
        "DEFAULT": "libluajit-5.1.so",
        "config//os:windows": "lua51.dll",
    }),
    srcs = [":build_luajit"],
    out = select({
        "DEFAULT": "libluajit-5.1.so",
        "config//os:windows": "lua51.dll",
    }),
)

select_file(
    name = "luajit-executable",
    filter = select({
        "DEFAULT": "bin/luajit",
        "config//os:windows": "bin\\luajit.exe",
    }),
    srcs = [":build_luajit"],
    out = select({
        "DEFAULT": "luajit",
        "config//os:windows": "luajit.exe",
    }),
)

select_file(
    name = "luajit-import-lib",
    filter = "lib\\lua51.lib",
    srcs = [":build_luajit"],
    out = "lua51.lib",
    target_compatible_with = ["config//os:windows"],
)

prebuilt_cxx_library(
    name = "luajit-lib",
    header_dirs = [":luajit-include-files"],
    shared_lib = ":luajit-shared-lib",
    import_lib = select({
        "DEFAULT": None,
        "config//os:windows": ":luajit-import-lib",
    }),
    header_namespace = "",
    visibility = ["PUBLIC"],
    target_compatible_with = ["config//os:windows"],
)

# We only want to link against the headers when building on linux,
# because linux often uses static linking where the symbols are found at
# runtime and do not need to be found at compile time
# Windows is the opposite - they need symbols at link time
prebuilt_cxx_library(
    name = "luajit-lib-headers-only",
    header_dirs = [":luajit-include-files"],
    header_namespace = "",
    visibility = ["PUBLIC"],
    target_compatible_with = ["config//os:linux"],
)

native.python_bootstrap_binary(
    name = "run_luajit.py",
    main = "run_luajit.py",
    visibility = ["PUBLIC"],
)

native.command_alias(
    name = "run_luajit",
    exe = ":run_luajit.py",
    args = ["--shared-lib", "$(location :luajit-shared-lib)", "--executable", "$(location :luajit-executable)"],
    visibility = ["PUBLIC"],
)

