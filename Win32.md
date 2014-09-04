How to build nixpy on Windows
=============================

The following guide shows build options for both, 32- and 64-bit. They are marked with :three::two: and :six::four: in the text.

Dependencies
------------

1. **Required prior to python build**
   - Navigate to the instructions for building nix on windows and follow the steps there to set up all necessary win build tools.

2. **Nix for windows**
   - Install nix for windows using the installer provided on github (https://github.com/G-Node/nix/releases), get the correct version (:three::two: or :six::four:)

3. **Python2.7**
   - Obtain python2.7.8 64-bit for windows, get the correct version (:three::two: or :six::four:)

4. **NumPy**:
   - :three::two: Get the 32-bit version of numpy from: http://sourceforge.net/projects/numpy/files/NumPy/
   - :six::four: Get the 64-bit version of numpy from: http://www.lfd.uci.edu/~gohlke/pythonlibs/#numpy

5. **Pip**:
   - Obtain "pip" for python2.7 (https://pip.pypa.io/en/latest/installing.html), get the correct version (:three::two: or :six::four:)
   - Add the pip directory to the windows PATH, it should e.g. be "C:\Python27\Scripts"

6. **Boost**:<br>
   Again, if you have not yet done so, head over to the instructions for building nix on windows to see how to build boost. Additionally we have to do the following:
   - Open `<BOOSTPATH>\boost\config\compiler\visualc.hpp` and look for a line "#define BOOST_NO_EXCEPTIONS". Disable it by commenting it out.
   - We need to rebuild boost with extended options compared to the nix build. Rebuild boost with:<br>
  :three::two:
    ```
     > .\b2 install -j4 -a --prefix=C:\opt\boost toolset=msvc architecture=x86 address-model=32 threading=multi variant=release link=static runtime-link=shared --with-python
    ```<br>
  :three::two:
    ```
     > .\b2 install -j4 -a --prefix=C:\opt\boost toolset=msvc architecture=x86 address-model=64 threading=multi variant=release link=static runtime-link=shared --with-python
    ```<br>
7. **Environment variables**:<br>
   Set the following environment variables using `set VAR=value` and `setx VAR "value" /m`. For the latter you will need to start a cmd window with admin rights. (right click the cmd icon and run as admin) Check if an environmental variable is set using `echo %VAR%`. If a variable should not seem to work try adding its' value to PATH too!
   - `BOOST_INCDIR = <PREFIX>` where `<PREFIX>` is the prefix used for building boost. NOTE: do _not_ use `<PREFIX>\include` as `BOOST_INCDIR` just `<PREFIX>`
   - `BOOST_LIBDIR = <PREFIX>\lib` where `<PREFIX>` is the prefix used for building boost.
   - `NIX_LIBDIR = <NIXPATH>\lib` where `<NIXPATH>` is the path where you installed nix using the windows installer. (e.g. "C:\Program Files (x86)\nix")
   - `NIX_INCDIR = <NIXPATH>\include` where `<NIXPATH>` is the path where you installed nix using the windows installer. (e.g. "C:\Program Files (x86)\nix")
   - `VS90COMNTOOLS = <VSPATH>\Common7\Tools` where `<VSPATH>` is the path where you installed visual studio. (e.g. "C:\Program Files (x86)\Microsoft Visual Studio 12.0")
   - `VS120COMNTOOLS = <VSPATH>\Common7\Tools` where `<VSPATH>` is the path where you installed visual studio. (e.g. "C:\Program Files (x86)\Microsoft Visual Studio 12.0") Make sure `<VSPATH>` is added to PATH too!

8. **vcvarsall.bat**:<br>
   :three::two:Execute once manually `vcvarsall.bat x86` from the cmd line.<br>
   :six::four:Execute once manually `vcvarsall.bat x86_amd64` from the cmd line.

9. **Build**:<br>
   Now build via:
    ```
    python setup.py build
    python setup.py bdist --format=msi
    ```
    afterwards you should have an installer in "dist\" and a "nix\core.pyd" file. NOTE: to make python build again delete the "core.pyd" file in "nix".

10. **Troubleshooting**:<br>
  - If you get a python error from "msvc9compiler.py", "query_vcvarsall" saying "ValueError: [u'path']" this means that "vcvarsall.bat" is not being found. Check the environmental vars and execute `vcvarsall.bat x86_amd64` manually.
  - If you get linker errors either the "boost_python" lib or the "nix" lib are not being found. Check the environmental vars and check whether "nix.lib" is in `<NIXPATH>\lib` and whether "boost_python-vc120-mt-1_55.lib" (with your version numbers) is in `<BOOSTPATH>\lib`

