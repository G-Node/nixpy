# Copyright (c) 2014, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

from __future__ import (absolute_import, division, print_function, unicode_literals)

import nix


class _cont(object):
    """
    Simple container for an element an a level
    """

    def __init__(self, elem, level):
        self.elem = elem
        self.level = level


def _find_sources(with_sources, filtr, limit):
    """
    Find a list of matching sources recursively.
    For internal use.
    """

    fifo = []
    result = []
    level = 0

    if isinstance(with_sources, nix.Source):
        fifo.append(_cont(with_sources, level))
    else:
        level += 1
        fifo += [_cont(e, level) for e in with_sources.sources]

    while len(fifo) > 0:
        c = fifo.pop(0)

        level = c.level + 1
        if level <= limit:
            fifo += [_cont(e, level) for e in c.elem.sources]

        if filtr(c.elem):
            result.append(c.elem)

    return result

def _find_sections(with_sections, filtr, limit):
    """
    Find a list of matching sections recursively.
    For internal use.
    """

    fifo = []
    result = []
    level = 0

    if isinstance(with_sections, nix.Section):
        fifo.append(_cont(with_sections, level))
    else:
        level += 1
        fifo += [_cont(e, level) for e in with_sections.sections]

    while len(fifo) > 0:
        c = fifo.pop(0)

        level = c.level + 1
        if level <= limit:
            fifo += [_cont(e, level) for e in c.elem.sections]

        if filtr(c.elem):
            result.append(c.elem)

    return result
