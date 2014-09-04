How to build nixpy on Windows
=============================

The following guide shows build options for both, 32- and 64-bit. They are marked with :three::two: and :six::four: in the text.

Dependencies
------------

1. **Required prior to python build**
   - Navigate to the instructions for building nix on windows and follow the steps there to set up all necessary win build tools.

2. **Nix for windows**
   - Install nix for windows in `C:\opt\nix` using the installer provided on github (https://github.com/G-Node/nix/releases), get the correct version (:three::two: or :six::four:)
   - Make sure `C:\opt\nix\bin` is added to the windows PATH

3. **Python2.7**
   - Obtain python2.7.8 64-bit for windows, get the correct version (:three::two: or :six::four:)
   - Make sure python is added to the windows PATH, e.g. `C:\Python27`

4. **NumPy**:
   - :three::two: Get the 32-bit version of numpy from: http://sourceforge.net/projects/numpy/files/NumPy/
   - :six::four: Get the 64-bit version of numpy from: http://www.lfd.uci.edu/~gohlke/pythonlibs/#numpy

5. **Pip**:
   - Obtain "pip" for python2.7 (https://pip.pypa.io/en/latest/installing.html), get the correct version (:three::two: or :six::four:)
   - Make sure pip is added to the windows PATH, e.g. `C:\Python27\Scripts`

6. **Boost**:<br>
   Again, if you have not yet done so, head over to the instructions for building nix on windows to see how to build boost. Additionally we have to do the following:
   - We need to rebuild boost with extended options compared to the nix build. Rebuild boost with:<br>
  :three::two:
    ```
     > .\b2 install -j4 -a --prefix=C:\opt\boost toolset=msvc architecture=x86 address-model=32 threading=multi variant=release link=static runtime-link=shared --with-python
    ```<br>
  :six::four:
    ```
     > .\b2 install -j4 -a --prefix=C:\opt\boost toolset=msvc architecture=x86 address-model=64 threading=multi variant=release link=static runtime-link=shared --with-python
    ```<br>
7. **Environment variables**:<br>
   Set the following environment variables using `set VAR=value` or `setx VAR "value" /m` to make them permanent. For the latter you will need to start a cmd window with admin rights. (right click the cmd icon and run as admin) Check if an environmental variable is set using `echo %VAR%`. If a variable should not seem to work try adding its' value to PATH too!
   - `BOOST_INCDIR = C:\opt\boost\include\boost-1_56` NOTE: insert your boost version for `1_56`
   - `BOOST_LIBDIR = C:\opt\boost\lib`
   - `NIX_LIBDIR = C:\opt\nix\lib`
   - `NIX_INCDIR = C:\opt\nix\include`
   - `VS90COMNTOOLS = <VSPATH>\Common7\Tools` where `<VSPATH>` is the path where you installed visual studio. (e.g. "C:\Program Files (x86)\Microsoft Visual Studio 12.0")
   - `VS120COMNTOOLS = <VSPATH>\Common7\Tools` where `<VSPATH>` is the path where you installed visual studio. (e.g. "C:\Program Files (x86)\Microsoft Visual Studio 12.0")
   - Make sure `<VSPATH>` is added to PATH too!

8. **vcvarsall.bat**:<br>
   :three::two:Execute once manually `vcvarsall.bat x86` from the cmd line.<br>
   :six::four:Execute once manually `vcvarsall.bat x86_amd64` from the cmd line.

9. **Build**:<br>
   NOTE: instead of steps 7. & 8. you can grab the code from 10. to set all vars. Make sure you are connected to the internet to allow missing packages to download. Now build via:
    ```
    python setup.py build
    python setup.py bdist --format=msi
    ```
    afterwards you should have an installer in "dist\" and a "nix\core.pyd" file. NOTE: to make python build again delete the "core.pyd" file in "nix".

10. **Troubleshooting**:<br>
  - If the PATH seems to be wrong (e.g. `python>>> import nix` fails with missing DLL) be sure to restart the Command Prompt _and_ restart Visual Studio before launching any Command Prompt from there
  - If you get a python error from "msvc9compiler.py", "query_vcvarsall" saying "ValueError: [u'path']" this means that "vcvarsall.bat" is not being found. Check the environmental vars and execute `vcvarsall.bat x86_amd64` manually.
  - If you get linker errors either the "boost_python" lib or the "nix" lib are not being found. Check the environmental vars and check whether "nix.lib" is in `<NIXPATH>\lib` and whether "boost_python-vc120-mt-1_55.lib" (with your version numbers) is in `<BOOSTPATH>\lib`
  - If you find steps 7. & 8. complicated grab this code, put it in a batch file and run it whenever you are about to build nixpy:<br>
  :three::two:
  ```
  set NIX_LIBDIR=C:\opt\nix\lib
  set NIX_INCDIR=C:\opt\nix\include
  set BOOST_LIBDIR=C:\opt\boost\lib
  set BOOST_INCDIR=C:\opt\boost\include\boost-1_56
  set VS90COMNTOOLS=C:\Program Files (x86)\Microsoft Visual Studio 12.0\Common7\Tools
  set VS120COMNTOOLS=C:\Program Files (x86)\Microsoft Visual Studio 12.0\Common7\Tools
  vcvarsall.bat x86
  ```
  :six::four:
  ```
  set NIX_LIBDIR=C:\opt\nix\lib
  set NIX_INCDIR=C:\opt\nix\include
  set BOOST_LIBDIR=C:\opt\boost\lib
  set BOOST_INCDIR=C:\opt\boost\include\boost-1_56
  set VS90COMNTOOLS=C:\Program Files (x86)\Microsoft Visual Studio 12.0\Common7\Tools
  set VS120COMNTOOLS=C:\Program Files (x86)\Microsoft Visual Studio 12.0\Common7\Tools
  vcvarsall.bat x86_amd64
  ```

