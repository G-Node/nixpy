==================================
NIXIO Python library documentation
==================================

|Build github| |Build appveyor| |Coverage coveralls| |Coverage codecov| |LGTM| |Docs|

.. |Build github| image:: https://github.com/G-Node/nixpy/workflows/NIXPy%20tests%20and%20linting/badge.svg?branch=master
    :target: https://github.com/G-Node/nixpy/actions
.. |Build appveyor| image:: https://ci.appveyor.com/api/projects/status/72l10ooxbvf0vfgd/branch/master?svg=true
    :target: https://ci.appveyor.com/project/G-Node/nixpy
.. |Coverage coveralls| image:: https://coveralls.io/repos/github/G-Node/nixpy/badge.svg?branch=master
    :target: https://coveralls.io/github/G-Node/nixpy?branch=master
.. |Coverage codecov| image:: https://codecov.io/gh/G-Node/nixpy/branch/master/graph/badge.svg?token=xT5rz1BlGJ
    :target: https://codecov.io/gh/G-Node/nixpy
.. |LGTM| image:: https://img.shields.io/lgtm/grade/python/g/G-Node/nixpy.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/G-Node/nixpy/context:python)
    :target: https://lgtm.com/projects/g/G-Node/nixpy
.. |Docs| image:: https://readthedocs.org/projects/nixpy/badge/?version=latest
    :target: https://nixpy.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

The NIXIO module is the native python re-implementation of the `NIX C++ library <https://nixio.readthedocs.io>`_ for the NIX data model.

The *NIX* data model allows to store fully annotated scientific
datasets, i.e. the data together with its metadata within the same
container. Our aim is to achieve standardization by providing a
common/generic data structure for a multitude of data types. See the
`wiki <https://github.com/G-Node/nix/wiki>`__ or the
`introduction <getting_started.html>`__ for more information.

The current implementations store the actual data using the
`HDF5 <http://www.hdfgroup.org/>`__ file format as a storage backend.

*NIX* emerged from the activities of the Electrophysiology Task Force of
the `INCF <http://www.incf.org>`__ Datasharing Program (2010-2015). It
is a registered research resource with the
`RRID:SCR_016196 <https://scicrunch.org/resources/Any/record/nlx_144509-1/SCR_016196/resolver?q=SCR_016196&l=SCR_016196>`__.

Introduction
============

We have assembled `introductory material <getting_started.html>`__
that illustrates using nix. The tutorials contain several code
examples. `The use_cases <https://nixio.readthedocs.io/en/master/use_cases.html>`__ explain in more detail how
nix is used in real world situations.

Support
=======
If you need help, want to get in touch, or have any other request
`these <contact.html>`__ are your options.

Citing
======

If you use *NIX*, it would be much appreciated if you would cite it in
publications with its identifier RRID:SCR_016196 and/or the reference:

*Stoewer A, Kellner CJ, Benda J, Wachtler T and Grewe J (2014). File
format and library for neuroscience data and metadata. Front.
Neuroinform. Conference Abstract: Neuroinformatics 2014. doi:
10.3389/conf.fninf.2014.18.00027*

Referenced by
=============
-  Sinz et al. (2020)
   `doi:10.1152/jn.00615.2019 <https://doi.org/10.1152/jn.00615.2019>`__
-  Buccino et al. (2019)
   `doi:10.1101/796599 <https://www.biorxiv.org/content/10.1101/796599v1>`__
-  Sprenger et al. (2019)
   `doi:10.3389/fninf.2019.00062 <https://doi.org/10.3389/fninf.2019.00062>`__
-  Dragly et al (2018)
   `doi:10.3389/fninf.2018.000169 <https://doi.org/10.3389/fninf.2018.000169>`__
-  Papez et al (2017)
   `doi:10.3389/fninf.2017.00024 <https://doi.org/10.3389/fninf.2017.00024>`__
-  Grewe et al (2017)
   `doi:10.1073/pnas.1615561114 <https://doi.org/10.1073/pnas.1615561114>`__
-  Vanek et al (2016)
   `doi:10.1109/informatics.2015.7377849 <https://doi.org/10.1109/informatics.2015.7377849>`__
-  Rübel et al (2016)
   `doi:10.3389/fninf.2016.00048 <https://doi.org/10.3389/fninf.2016.00048>`__
-  Denker et al (2016)
   `doi:10.1007/978-3-319-50862-7_5 <https://doi.org/doi:10.1007/978-3-319-50862-7_5>`__
-  Teeters et al (2015)
   `doi:10.1016/j.neuron.2015.10.025 <https://doi.org/doi:10.1016/j.neuron.2015.10.025>`__

.. toctree::
   :caption: Introduction
   :maxdepth: 1

   basic_idea
   install
   standardization
   Use-cases <https://nixio.readthedocs.io/en/master/use_cases.html>

.. toctree::
   :maxdepth: 1
   :caption: News
   :hidden:

   news

.. toctree::
   :maxdepth: 1
   :caption: Tutorials

   getting_started

.. toctree::
   :caption: Troubleshooting:
   :maxdepth: 1
   :hidden:

   contact
   faq

.. toctree::
   :maxdepth: 1
   :caption: API Reference
   :hidden:

   user_api
   api/nixio

.. toctree::
   :caption: Appendix
   :maxdepth: 1
   :hidden:

   genindex
   py-modindex
   Sources on GitHub <https://github.com/g-node/nixpy>
   License <https://github.com/G-Node/nixpy/blob/master/LICENSE>
   Contributing guide <https://github.com/G-Node/nix/blob/master/CONTRIBUTING.md>
