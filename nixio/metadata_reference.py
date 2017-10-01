# Copyright (c) 2016, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

from .section import Section


def create_metadata_prop():

    doc = ("Associated metadata of the entity. Sections attached to the entity"
           "via this attribute can provide additional annotations. This is an"
           "optional read-write property, and can be None if no metadata is"
           "available."

           ":type: Section")

    def getmd(self):
        if "metadata" in self._h5group:
            return Section(None, self._h5group.open_group("metadata"))
        else:
            return None

    def setmd(self, sect):
        if not isinstance(sect, Section):
            raise TypeError("{} is not of type Section".format(sect))
        self._h5group.create_link(sect, "metadata")

    def rmmd(self):
        if "metadata" in self._h5group:
            self._h5group.delete("metadata")

    return property(fget=getmd, fset=setmd, fdel=rmmd, doc=doc)
