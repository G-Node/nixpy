# NIX Features and Changes

This document outlines the features that have been implemented in NIX and have not yet been added to NIXPy.
The features are separated into two sections: Released features and Unreleased ones. The latter is for features that exist in nix/master but have yet to be included in a stable release.

# Released

## Data compression

NIX PR: [#695](https://github.com/G-Node/nix/pull/695)

NIXPy Issue: [#277](https://github.com/G-Node/nixpy/issues/277)

Introduced in [NIX Version 1.4.1](https://github.com/G-Node/nix/releases/tag/1.4.1)

Description: Exposes HD5's dataset compression support through the NIX DataArray creation API.

Note: NIXPy can currently load files with compressed datasets and writing to an existing compressed dataset should work without issues, since H5Py supports this. However, there is no way to create a compressed dataset through NIXPy since the options aren't exposed anywhere in the NIXPy API.

# Unreleased

## DataFrame

NIX PR: [#708](https://github.com/G-Node/nix/pull/708)

Description: A new object type called DataFrame for tabular data.

## Retrieve multiple tagged data slices in one go

NIX PR: [#722](https://github.com/G-Node/nix/pull/722)

Description: Retrieve multiple tagged slices with one call to the retrieveData function. This can save a considerable amount overhead that would occur if multiple calls were made.

NIXPy Issue: [#285](https://github.com/G-Node/nixpy/issues/285)

## Remove Values and move Uncertainty to Property

NIX PR: [#723](https://github.com/G-Node/nix/pull/723)

NIXPy Issue: [#301](https://github.com/G-Node/nixpy/issue/301)

Description: Metadata Values are no longer a compound data type. The Property object is now a dataset with a simple data type.
