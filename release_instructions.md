# Checklist for NIXPY release

Most of the following steps are checked and performed by the [release script](scripts/dorelease.py).

1. Create branch (if necessary)  
   For releases with breaking changes (e.g., 1.2.0, 1.3.0, etc, see the [NIX API and file format versioning](https://github.com/G-Node/nix/blob/master/docs/versioning.md) guide) create a new branch called `vX.Y` (e.g., `v1.2`).
   This is not necessary for minor releases with non-breaking changes (e.g., `1.2.0 → 1.2.1`)
2. Tag with release version  
   Tag the latest commit with the full version number (e.g., `1.2.1`).
3. Update readme  
   Change the Travis, and Coverage badges in the readme to point to the status of the new branch.
4. Change CI configurations  
   Travis and Appveyor configurations should be changed so that the new nixpy branch builds using the corresponding nix branch.
5. Increment version number in info.py
6. Upload to PyPI  
   Upload source archive using:
   ```
   $ python setup.py sdist
   $ twine upload dist/nixio-X.Y.Z.tar.gz
   ```

   Upload Windows wheels, found in Appveyor artifacts.
7. Create [release on GitHub](https://github.com/G-Node/nixpy/releases).
