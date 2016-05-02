# Copyright (c) 2014, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

from __future__ import (absolute_import, division, print_function, unicode_literals)

from nixio.core import Property
from nixio.util.inject import inject
from nixio.value import Value
from nixio.core import CValue, CDataType


class PropertyMixin(Property):

    @property
    def values(self):
        values = self._values
        return [Value(v.value) for v in values]

    @values.setter
    def values(self, values):
        self._values = [CValue(v.value) for v in values]

    @property
    def data_type(self):
        dtype = self._data_type
        if isinstance(dtype, CDataType):
            return Value.dtype_from_c(dtype)
        else:
            return dtype

    def __eq__(self, other):
        if hasattr(other, "id"):
            return self.id == other.id
        else:
            return False

    def __hash__(self):
        """
        overwriting method __eq__ blocks inheritance of __hash__ in Python 3
        hash has to be either explicitly inherited from parent class, implemented or escaped
        """
        return hash(self.id)

inject((Property,), dict(PropertyMixin.__dict__))
