class DuplicateName(Exception):

    def __init__(self, caller, *args, **kwargs):
        self.message = ("Duplicate name - "
                        "names have to be unique for a given "
                        "entity type & parent. ({})").format(caller)
        super(DuplicateName, self).__init__(self.message, *args, **kwargs)


class UninitializedEntity(Exception):

    def __init__(self, *args, **kwargs):
        self.message = "The Entity being accessed is uninitialized or empty."
        super(UninitializedEntity, self).__init__(self.message, *args, **kwargs)


class InvalidUnit(Exception):

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
