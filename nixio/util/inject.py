from __future__ import (absolute_import, division, print_function,
                        unicode_literals)


excludes = ("__module__", "__metaclass__", "__dict__", "__doc__")

""" 
Does monkey patching to the classes in 'bases' by adding
methods from the given dict 'dct'.
"""
def inject(bases, dct):
    for base in bases:
        for k,v in dct.items():
            if k not in excludes:
                setattr(base, k, v)

