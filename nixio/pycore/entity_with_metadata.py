# Copyright (c) 2016, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

from .entity import NamedEntity
from .section import Section


class EntityWithMetadata(NamedEntity):

    def __init__(self, nixparent, h5group):
        super(EntityWithMetadata, self).__init__(nixparent, h5group)
        # TODO: Additional validation for metadata

    @classmethod
    def _create_new(cls, nixparent, h5parent, name, type_):
        newentity = super(EntityWithMetadata, cls)._create_new(
            nixparent, h5parent, name, type_
        )
        return newentity

    @property
    def metadata(self):
        """
        Associated metadata of the entity. Sections attached to the entity
        via this attribute can provide additional annotations. This is an
        optional read-write property, and can be None if no metadata is
        available.

        :type: Section
        """
        if "metadata" in self._h5group:
            mdsection = Section(None, self._h5group.open_group("metadata"))
            return mdsection
            # This is extremely inefficient and makes writing and reading of
            # files which contain a large number of objects very slow.
            # In fact, it makes things increasingly slow, which amplifies
            # the existing issue https://github.com/G-Node/nixpy/issues/165

            # Disabling parent reference temporarily

            # sectionid = mdsection.id

            # rootmd = self._h5group.file.open_group("metadata")
            # results = []
            # for sectgroup in rootmd:
            #     sect = Section(None, sectgroup)
            #     results.extend(
            #         sect.find_sections(filtr=lambda x: x.id == sectionid)
            #     )
            # if results:
            #     return results[0]
            # else:
            #     raise RuntimeError("Invalid metadata found in {}".
            #                        format(self))
        else:
            return None

    @metadata.setter
    def metadata(self, sect):
        if not isinstance(sect, Section):
            raise TypeError("Error setting metadata to {}. Not a Section."
                            .format(sect))
        self._h5group.create_link(sect, "metadata")

