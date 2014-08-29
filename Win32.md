How to build nixpy on Win32
===========================

NB: Currently only Relase type builds on Windows x64 have been successfully tested.

Dependencies
------------

0) Required prior to python build
   - Navigate to the instructions for building nix on windows and follow the steps there to set up all necessary win build tools.

1) **Nix for windows**
   - Install nix for windows using the installer provided on github (https://github.com/G-Node/nix/releases)

2) **Python2.7**
   - Obtain python2.7.8 64-bit for windows (important: do not confuse with 32-bit version!)

3) **NumPy 64-bit**:
   - For the 64-bit python we will need a 64-bit numpy version. Get it from: http://www.lfd.uci.edu/~gohlke/pythonlibs/#numpy

3) **Pip**:
   - Obtain "pip" for python2.7 64-bit (https://pip.pypa.io/en/latest/installing.html)
   - Add the pip directory to the windows PATH, it should e.g. be "C:\Python27\Scripts"

4) **Boost**:
   Again, if you have not yet done so, head over to the instructions for building nix on windows to see how to build boost. Additionally we have to do the following:
   - Open `<BOOSTPATH>\boost\config\compiler\visualc.hpp` and look for a line "#define BOOST_NO_EXCEPTIONS". Disable it by commenting it out.
   - We need to rebuild boost with extended options compared to the nix build. We will need to modify the boost build command to be:

```
.\b2 --toolset=msvc-12.0 threading=multi variant=release architecture=x86 address-model=64 --prefix=<PREFIX> --libdir=<PREFIX>\lib --include-dir=<PREFIX>\include -j4 --build-type=complete --with-python --with-date_time --with-regex --with-filesystem --with-program_options --with-system --with-exception install
```

5) **Environment variables**:
   Set the following environment variables using `set VAR=value` and `setx VAR "value" /m`. For the latter you will need to start a cmd window with admin rights. (right click the cmd icon and run as admin) Check if an environmental variable is set using `echo %VAR%`. If a variable should not seem to work try adding its' value to PATH too!
   - `BOOST_INCDIR = <PREFIX>` where `<PREFIX>` is the prefix used for building boost. NOTE: do _not_ use `<PREFIX>\include` as `BOOST_INCDIR` just `<PREFIX>`
   - `BOOST_LIBDIR = <PREFIX>\lib` where `<PREFIX>` is the prefix used for building boost.
   - `NIX_LIBDIR = <NIXPATH>\lib` where `<NIXPATH>` is the path where you installed nix using the windows installer. (e.g. "C:\Program Files (x86)\nix")
   - `NIX_INCDIR = <NIXPATH>\include` where `<NIXPATH>` is the path where you installed nix using the windows installer. (e.g. "C:\Program Files (x86)\nix")
   - `VS90COMNTOOLS = <VSPATH>\Common7\Tools` where `<VSPATH>` is the path where you installed visual studio. (e.g. "C:\Program Files (x86)\Microsoft Visual Studio 12.0")
   - `VS120COMNTOOLS = <VSPATH>\Common7\Tools` where `<VSPATH>` is the path where you installed visual studio. (e.g. "C:\Program Files (x86)\Microsoft Visual Studio 12.0") Make sure `<VSPATH>` is added to PATH too!

6) **vcvarsall.bat**:
   Execute once manually `vcvarsall.bat x86_amd64` from the cmd line.

7) **vcvarsall.bat**:
   Now build via:

```
python setup.py build
python setup.py bdist --format=msi
```

afterwards you should have an installer in "dist\" and a "nix\core.pyd" file. NOTE: to make python build again delete the "core.pyd" file in "nix".


**Troubleshooting**:

- If you get a python error from "msvc9compiler.py", "query_vcvarsall" saying "ValueError: [u'path']" this means that "vcvarsall.bat" is not being found. Check the environmental vars and execute `vcvarsall.bat x86_amd64` manually.
- If you get linker errors either the "boost_python" lib or the "nix" lib are not being found. Check the environmental vars and check whether "nix.lib" is in `<NIXPATH>\lib` and whether "boost_python-vc120-mt-1_55.lib" (with your version numbers) is in `<BOOSTPATH>\lib`

