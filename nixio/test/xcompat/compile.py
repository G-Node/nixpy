# -*- coding: utf-8 -*-
# Copyright © 2018, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.
import sys
import os
import platform
from glob import glob

import distutils.sysconfig
from distutils import ccompiler
from distutils.errors import CompileError, LinkError


WINDOWS = False
if platform.platform().startswith("Windows"):
    WINDOWS = True


def cc(filenames, dest,
       library_dirs=None, include_dirs=None,
       libraries=None, compile_args=None,
       runtime_lib_dirs=None):
    compiler = ccompiler.new_compiler()

    distutils.sysconfig.customize_compiler(compiler)
    if library_dirs:
        [compiler.add_library_dir(libd) for libd in library_dirs]
    if include_dirs:
        [compiler.add_include_dir(incd) for incd in include_dirs]
    if libraries:
        [compiler.add_library(lib) for lib in libraries]
    if runtime_lib_dirs and not WINDOWS:
        [compiler.add_runtime_library_dir(rund) for rund in runtime_lib_dirs]

    try:
        for srcname in filenames:
            execname, ext = os.path.splitext(srcname)
            compiler.link_executable(
                [srcname], execname, output_dir=dest,
                extra_postargs=compile_args,
                target_lang="c++",
            )
    except (CompileError, LinkError):
        return False
    return True


def maketests(dest):
    scriptloc, _ = os.path.split(os.path.abspath(__file__))
    os.chdir(scriptloc)
    filenames = glob("*.cpp")
    nix_inc_dir = os.getenv('NIX_INCDIR', '/usr/local/include')
    nix_lib_dir = os.getenv('NIX_LIBDIR', '/usr/local/lib')

    boost_inc_dir = os.getenv('BOOST_INCDIR', '/usr/local/include')
    boost_lib_dir = os.getenv('BOOST_LIBDIR', '/usr/local/lib')
    library_dirs = [boost_lib_dir, nix_lib_dir]
    include_dirs = [boost_inc_dir, nix_inc_dir, 'src']
    runtime_dirs = ["/usr/local/lib"]
    llp = os.getenv("LD_LIBRARY_PATH", None)
    if llp is not None:
        runtime_dirs.append(llp)
    libraries = ["nix"]
    compile_args = ["--std=c++11"]
    if WINDOWS:
        compile_args = []
        libraries = ["nixio"]

    print("Compiling {}".format(" ".join(filenames)))
    success = cc(filenames, dest,
                 library_dirs=library_dirs,
                 include_dirs=include_dirs,
                 libraries=libraries,
                 compile_args=compile_args,
                 runtime_lib_dirs=runtime_dirs)
    if success:
        print("Done")
    else:
        print("Failed")
    return success


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Need a target dir")
        sys.exit(1)

    dest = sys.argv[1]
    sys.exit(not maketests(dest))
