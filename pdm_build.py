import os
from enum import Enum
from typing import Any, Dict

from pdm.backend.hooks import Context
from setuptools import Distribution, Extension


class Compiler(str, Enum):
    CLANG = "clang"
    GCC = "gcc"
    MSVC = "msvc"

BUILD_FLAGS = {
    Compiler.CLANG: [
        "-std=c++20",
    ],
    Compiler.GCC: [
        "-std=c++20",
    ],
    Compiler.MSVC: [
    ],
}

COVERAGE_FLAGS = {
    Compiler.CLANG: [
        "-fprofile-instr-generate",
        "-fcoverage-mapping",
    ],
    Compiler.GCC: ["--coverage"],
    Compiler.MSVC: ["/source-charset:utf-8", "/Zi", "/DEBUG"],
}


def pdm_build_hook_enabled(context: Context) -> bool:
    return context.target in ("wheel", "editable")


def pdm_build_update_setup_kwargs(
    context: Context, setup_kwargs: Dict[str, Any]
) -> None:
    sources = [
        "src/levdist/_native.cpp",
    ]

    compiler = _get_compiler()
    extra_compile_args = BUILD_FLAGS.get(compiler, [])

    if os.environ.get("WITH_COVERAGE") is not None:
        extra_compile_args.extend(COVERAGE_FLAGS.get(_get_compiler(), []))


    setup_kwargs.update(
        ext_modules=[
            Extension(
                name="levdist._native",
                sources=sources,
                extra_compile_args=extra_compile_args,
                extra_link_args=extra_compile_args,
            )
        ]
    )


def _get_compiler() -> Compiler:
    d = Distribution()
    build_ext = d.get_command_obj("build_ext")
    build_ext.finalize_options()
    # register an extension to ensure a compiler is created
    build_ext.extensions = [Extension("ignored", ["ignored.c"])]
    # disable building fake extensions
    build_ext.build_extensions = lambda: None
    # run to populate self.compiler
    build_ext.run()
    compiler = build_ext.compiler
    if hasattr(compiler, "compiler"):
        return Compiler(build_ext.compiler.compiler[0])
    elif compiler.compiler_type == "msvc":
        return Compiler.MSVC

    print(f"Unsupported compiler {compiler} {compiler.compiler_type}")
    raise RuntimeError("Unsupported compiler")
