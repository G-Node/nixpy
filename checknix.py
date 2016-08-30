import os, sys
from textwrap import dedent
import tempfile

import distutils.sysconfig
import distutils.ccompiler
from distutils.errors import CompileError, LinkError


def check_nix(libdirs=(), incdirs=()):
    """
    Check if NIX is available by trying to compile a tiny program.
    """

    cpp_code = dedent("""
    #include <nix.hpp>

    int main() {
        return 0;
    }
    """)
    with tempfile.TemporaryDirectory() as tmpdir:
        bin_file_name = os.path.join(tmpdir, "check_nix")
        file_name = bin_file_name + '.cpp'
        with open(file_name, 'w') as cfile:
            cfile.write(cpp_code)

        compiler = distutils.ccompiler.new_compiler()
        assert isinstance(compiler, distutils.ccompiler.CCompiler)

        compiler.library_dirs.extend(libdirs)
        compiler.include_dirs.extend(incdirs)
        distutils.sysconfig.customize_compiler(compiler)

        # stderr = os.dup(sys.stderr.fileno())
        errfile = open(os.path.join(tmpdir, "check_nix.err"), 'w')
        os.dup2(errfile.fileno(), sys.stderr.fileno())
        try:
            compiler.compile([file_name])
        except (CompileError, LinkError):
            ret_val = False
        else:
            ret_val = True
        errfile.close()
    return ret_val


if __name__ == '__main__':
    nix_inc_dir = os.getenv('NIX_INCDIR', '/usr/local/include')
    nix_lib_dir = os.getenv('NIX_LIBDIR', '/usr/local/lib')
    res = check_nix([nix_lib_dir], [nix_inc_dir])
    if res:
        print("Found NIX.")
    else:
        print("NIX not found.")


