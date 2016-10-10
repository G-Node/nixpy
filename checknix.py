import os, sys, shutil

from textwrap import dedent
import tempfile

import distutils.sysconfig
import distutils.ccompiler
from distutils.errors import CompileError, LinkError


def check_nix(library_dirs=(), include_dirs=(), compile_args=()):
    """
    Check if NIX is available by trying to compile a tiny program.
    """

    cpp_code = dedent("""
    #include <nix.hpp>

    int main() {
        return 0;
    }
    """)

    tmpdir = tempfile.mkdtemp()
    bin_file_name = os.path.join(tmpdir, "check_nix")
    file_name = bin_file_name + '.cpp'
    with open(file_name, 'w') as cfile:
        cfile.write(cpp_code)

    compiler = distutils.ccompiler.new_compiler()
    assert isinstance(compiler, distutils.ccompiler.CCompiler)

    distutils.sysconfig.customize_compiler(compiler)
    compiler.set_library_dirs(library_dirs)
    compiler.set_include_dirs(include_dirs)

    stderr = os.dup(sys.stderr.fileno())
    errfile = open(os.path.join(tmpdir, "check_nix.err"), 'w')
    # redirect stderr to file
    os.dup2(errfile.fileno(), sys.stderr.fileno())
    try:
        compiler.compile([file_name], output_dir=tmpdir,
                         extra_postargs=compile_args)
    except (CompileError, LinkError):
        ret_val = False
    else:
        ret_val = True
    # restore stderr
    os.dup2(stderr, sys.stderr.fileno())
    errfile.close()
    shutil.rmtree(tmpdir)
    return ret_val


if __name__ == '__main__':
    nix_inc_dir = os.getenv('NIX_INCDIR', '/usr/local/include')
    nix_lib_dir = os.getenv('NIX_LIBDIR', '/usr/local/lib')
    res = check_nix([nix_lib_dir], [nix_inc_dir])
    if res:
        print("Found NIX.")
    else:
        print("NIX not found.")


