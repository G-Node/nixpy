# Copyright (c) 2014, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

import nixio


class Cont(object):
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

    sourcecls = (nixio.pycore.Source,)
    try:
        sourcecls += (nixio.core.Source,)
    except AttributeError:
        pass

    if isinstance(with_sources, sourcecls):
        fifo.append(Cont(with_sources, level))
    else:
        level += 1
        fifo += [Cont(e, level) for e in with_sources.sources]

    while len(fifo) > 0:
        c = fifo.pop(0)

        level = c.level + 1
        if level <= limit:
            fifo += [Cont(e, level) for e in c.elem.sources]

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

    sectioncls = (nixio.pycore.Section,)
    try:
        sectioncls += (nixio.core.Section,)
    except AttributeError:
        pass

    if isinstance(with_sections, sectioncls):
        fifo.append(Cont(with_sections, level))
    else:
        level += 1
        fifo += [Cont(e, level) for e in with_sections.sections]

    while len(fifo) > 0:
        c = fifo.pop(0)

        level = c.level + 1
        if level <= limit:
            fifo += [Cont(e, level) for e in c.elem.sections]

        if filtr(c.elem):
            result.append(c.elem)

    return result
