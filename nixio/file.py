# Copyright (c) 2014, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import nixio.util.find as finders
from nixio.util.proxy_list import ProxyList

try:
    from sys import maxint
except:
    from sys import maxsize as maxint
