class Inject(object):
    """
    Class that can be used as a metaclass in order to ease monkey patching.

    Using Inject as metaclass has the effect, that all methods from the
    class where it was uses will be added (monkey patched) to its base classes.

    Usage:

    >>> class Foo(Bar):
    >>>     class __metaclass__(Inject):
    >>>          pass

    The above code will inject all methods from Foo into Bar as soon as
    Foo is imported.
    """

    def __init__(self, name, bases, dict):
        excludes = ("__module__", "__metaclass__")

        for b in bases:
            if type(b) not in (self, type):
                for k,v in dict.items():
                    if k not in excludes:
                        setattr(b,k,v)
