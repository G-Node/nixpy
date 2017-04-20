from collections import Iterable
from . import util


try:
    strtype = basestring
except NameError:
    strtype = str


class Container(object):
    """
    Container acts as an interface to container groups in the backend. In the
    case of HDF5, this is a group that is used as a container for other groups.

    Most methods of this class are simple interfaces to the respective methods
    of the backend class (e.g., H5Group).

    Examples of containers:
        Block.data_arrays
        Block.tags
        Block.multi_tags
        Source.sources
    """

    def __init__(self, name, parent, itemclass):
        self._backend = parent.open_group(name)
        self._itemclass = itemclass
        self._parent = parent

    def __len__(self):
        return len(self._backend)

    def __getitem__(self, item):
        if isinstance(item, int):
            if item < 0:
                item = len(self) + item
            if item < 0 or item >= len(self):
                raise IndexError("Index out of bounds: {} ({})".format(item))
            item = self._backend.get_by_pos(item)
        else:
            item = self._backend.get_by_id_or_name(item)
        return self._itemclass(self._parent, item)

    def __delitem__(self, item):
        if isinstance(item, int):
            item = self._backend.get_by_pos(item).name
        self._backend.delete(item)

    def __iter__(self):
        for group in self._backend:
            yield self._itemclass(self._parent, group)

    def __contains__(self, item):
        if isinstance(item, strtype):
            try:
                self[item]
                return True
            except ValueError:
                return False
        else:
            return item.name in self._backend

    def __str__(self):
        return "[{}]".format(
            ", ".join(str(item) for item in self)
        )

    def __repr__(self):
        return str(self)


class LinkContainer(Container):
    def __init__(self, name, parent):
        self._backend = parent.open_group(name)

    def append(self, item):
        if util.is_uuid(item):
            item = self._backend.get_by_id(item)

        if not hasattr(item, "id"):
            self._backend.create_link(item, item.id)
        else:
            raise TypeError("NIX entity or id string required for append")

    def extend(self, items):
        if not isinstance(items, Iterable):
            raise TypeError("{} object is not iterable".format(type(items)))
        for item in items:
            self.append(item)
