# Copyright (c) 2014, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

from nixio.tag import ReferenceProxyList, FeatureProxyList


class MultiTagMixin(object):

    @property
    def references(self):
        """
        A property containing all data arrays referenced by the tag. Referenced
        data arrays can be obtained by index or their id. References can be
        removed from the list, removing a referenced DataArray will not remove
        it from the file. New references can be added using the append method
        of the list.
        This is a read only attribute.

        :type: RefProxyList of DataArray
        """
        if not hasattr(self, "_references"):
            setattr(self, "_references", ReferenceProxyList(self))
        return self._references

    @property
    def features(self):
        """
        A property containing all features of the tag. Features can be obtained
        via their index or their id. Features can be deleted from the list.
        Adding new features to the tag is done using the create_feature method.
        This is a read only attribute.

        :type: ProxyList of Feature.
        """
        if not hasattr(self, "_features"):
            setattr(self, "_features", FeatureProxyList(self))
        return self._features
