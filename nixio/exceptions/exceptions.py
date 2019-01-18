# -*- coding: utf-8 -*-
# Copyright © 2016, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.


class DuplicateName(Exception):

    def __init__(self, caller, *args, **kwargs):
        self.message = ("Duplicate name - "
                        "names have to be unique for a given "
                        "entity type & parent. ({})").format(caller)
        super(DuplicateName, self).__init__(self.message, *args, **kwargs)


class UninitializedEntity(Exception):

    def __init__(self, *args, **kwargs):
        self.message = "The Entity being accessed is uninitialized or empty."
        super(UninitializedEntity, self).__init__(self.message,
                                                  *args, **kwargs)


class InvalidUnit(ValueError):

    def __init__(self, what, where):
        self.message = "InvalidUnit: {} evoked at: {}".format(what, where)
        super(InvalidUnit, self).__init__(self.message)


class InvalidAttrType(TypeError):

    def __init__(self, type_, value):
        self.message = ("Attribute requires type {} but {} "
                        "was provided.".format(type_, type(value)))
        super(InvalidAttrType, self).__init__(self.message)


class InvalidEntity(Exception):

    def __init__(self, *args, **kwargs):
        self.message = "Invalid entity found in HDF5 file."
        super(InvalidEntity, self).__init__(self.message, *args, **kwargs)


class OutOfBounds(IndexError):

    def __init__(self, message, index=None):
        self.message = message
        if index is not None:
            self.message += " [at index: {}]".format(index)
        super(OutOfBounds, self).__init__(self.message)


class IncompatibleDimensions(ValueError):

    def __init__(self, what, where):
        self.message = "IncompatibleDimensions: {} evoked at: {})".format(
            what, where
        )
        super(IncompatibleDimensions, self).__init__(self.message)


class InvalidFile(Exception):

    def __init__(self):
        self.message = "Invalid file - file is not a nix file."
        super(InvalidFile, self).__init__(self.message)
