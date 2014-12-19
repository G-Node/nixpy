# Copyright (c) 2014, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

from __future__ import (absolute_import, division, print_function, unicode_literals)

from nix.core import Property, Value
from nix.util.inject import Inject

class PropertyMixin(Property):

    class __metaclass__(Inject, Property.__class__):
        pass

    def __eq__(self, other):
        if hasattr(other, "id"):
            return self.id == other.id
        else:
            return False

    def __hash__(self):
        """
        overwriting method __eq__ blocks inheritance of __hash__ in Python 3
        hash has to be either explicitly inherited from parent class or escaped
        """
        __hash__ = Property.__hash__


class ValueMixin(Value):

    class __metaclass__(Inject, Value.__class__):
        pass

    def __eq__(self, other):
        if hasattr(other, "value"):
            return self.value == other.value
        else:
            return self.value == other

    def __hash__(self):
        """
        overwriting method __eq__ blocks inheritance of __hash__ in Python 3
        hash has to be either explicitly inherited from parent class or escaped
        """
        __hash__ = Value.__hash__
