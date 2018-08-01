from .entity import Entity
from collections import Iterable
from . import util


class Container(object):
    """
    Container acts as an interface to container groups in the backend. In the
    case of HDF5, this is a group that is used as a container for other groups.

    Examples of Containers:
        Block.data_arrays
        Block.tags
        Block.multi_tags
        Source.sources

    :param name: Name of the container
    :param parent: Parent NIX object where this container will be created
    :param itemclass: The class of the objects this container holds (for
    checking and instantiations)
    """

    def __init__(self, name, parent, itemclass):
        self._backend = parent._h5group.open_group(name)
        self._itemclass = itemclass
        self._parent = parent
        self._name = name

    def _inst_item(self, item):
        return self._itemclass(self._parent, item)

    def __len__(self):
        return len(self._backend)

    def __getitem__(self, item):
        if isinstance(item, int):
            if item < 0:
                item = len(self) + item
            if item < 0 or item >= len(self):
                raise IndexError("Index out of bounds: {}".format(item))
            item = self._backend.get_by_pos(item)
        else:
            item = self._backend.get_by_id_or_name(item)
        return self._inst_item(item)

    def __delitem__(self, item):
        if not isinstance(item, Entity):
            item = self[item]

        if not isinstance(item, self._itemclass):
            raise TypeError(
                "Wrong item type: {} required or the name or ID of one".format(
                    self._itemclass.__name__)
            )

        root = self._backend.h5root
        if not root:
            root = self._parent._h5group
        root.delete_all([item.id])

    def __iter__(self):
        for group in self._backend:
            yield self._inst_item(group)

    def __contains__(self, item):
        if hasattr(item, "id"):
            if isinstance(item, self._itemclass):
                return item.name in self._backend
            # looks like a NIX object, but wrong type
            raise TypeError(
                "Wrong item type: {} required or the name or ID of one".format(
                    self._itemclass.__name__)
            )
        if util.is_uuid(item):
            try:
                self._backend.get_by_id(item)
                return True
            except KeyError:
                return False
        else:
            return item in self._backend

    def __str__(self):
        return "[{}]".format(
            ", ".join(str(item) for item in self)
        )

    def __repr__(self):
        return str(self)

    @staticmethod
    def _item_key(item):
        return item.name

    def items(self):
        for group in self._backend:
            item = self._inst_item(group)
            yield item.id, item


class SectionContainer(Container):
    """
    SectionContainer extends Container with a new __delitem__ method.
    When a Section is deleted, all child sections need to be deleted
    individually to make sure all their references are removed.
    """
    def __delitem__(self, item):
        if not isinstance(item, Entity):
            item = self[item]

        if not isinstance(item, self._itemclass):
            raise TypeError(
                "Wrong item type: {} required or the name or ID of one".format(
                    self._itemclass.__name__)
            )

        # collect all IDs under item and send them for deletion, starting from
        # the root block
        secids = [s.id for s in item.find_sections()]

        root = self._backend.file
        root.delete_all(secids)


class SourceContainer(Container):
    """
    SourceContainer extends Container with a new __delitem__ method.
    When a Source is deleted, all child sources need to be deleted individually
    to make sure all their references are removed.
    """
    def __delitem__(self, item):
        if not isinstance(item, Entity):
            item = self[item]

        if not isinstance(item, self._itemclass):
            raise TypeError(
                "Wrong item type: {} required or the name or ID of one".format(
                    self._itemclass.__name__)
            )

        # collect all IDs under item and send them for deletion, starting from
        # the root block
        srcids = [s.id for s in item.find_sources()]
        srcids.append(item.id)

        root = self._backend.h5root
        root.delete_all(srcids)


class LinkContainer(Container):
    """
    A LinkContainer acts as an interface to container groups in the backend
    that hold links to objects already contained in a Container.

    Objects are added to a LinkContainer using the 'append' method, as
    opposed to Containers which get populated by the parent object 'create'
    methods.

    An important difference between a LinkContainer and a Container is that
    links to objects are indexed by their 'id' whereas objects in Containers
    are indexed by 'name'.

    Examples of LinkContainers:
        Group.data_arrays
        Group.tags
        Group.multi_tags

    :param name: Name of the container
    :param parent: Parent H5Group where this container will be created
    :param itemclass: The class of the objects this container holds (for
    checking and instantiations)
    :param itemstore: The location (Container) where the original objects
    are stored and linked to.
    """

    def __init__(self, name, parent, itemclass, itemstore):
        super(LinkContainer, self).__init__(name, parent, itemclass)
        self._itemstore = itemstore

    def __delitem__(self, item):
        if not isinstance(item, Entity):
            item = self[item]

        if not isinstance(item, self._itemclass):
            raise TypeError(
                "Wrong item type: {} required or the name or ID of one".format(
                    self._itemclass.__name__)
            )

        self._backend.delete(item.id)

    def append(self, item):
        if util.is_uuid(item):
            item = self._inst_item(self._backend.get_by_id(item))

        if not hasattr(item, "id"):
            raise TypeError("NIX entity or id string required for append")

        if item not in self._itemstore:
            raise RuntimeError("This item cannot be appended here.")

        self._backend.create_link(item, item.id)

    def extend(self, items):
        if not isinstance(items, Iterable):
            raise TypeError("{} object is not iterable".format(type(items)))
        for item in items:
            self.append(item)

    def __getitem__(self, identifier):
        if isinstance(identifier, int):
            return super(LinkContainer, self).__getitem__(identifier)
        else:
            if util.is_uuid(identifier):
                # For LinkContainer, name is id
                item = self._backend.get_by_name(identifier)
                return self._inst_item(item)
            else:
                for grp in self._backend:
                    if identifier == grp.get_attr("name"):
                        return self._inst_item(grp)
                else:
                    raise KeyError("Item not found '{}'".format(identifier))

    def __contains__(self, item):
        # need to redefine because of id indexing/linking
        if hasattr(item, "id"):
            if isinstance(item, self._itemclass):
                return item.id in self._backend
            # looks like a NIX object, but wrong type
            raise TypeError(
                "Wrong item type: {} required or the name or ID of one".format(
                    self._itemclass.__name__)
            )

        if util.is_uuid(item):
            return item in self._backend

        # assume it's a name and scan through LinkContainer
        for grp in self._backend:
            if item == grp.get_attr("name"):
                return True
        return False

    def _inst_item(self, item):
        return self._itemclass(self._itemstore._parent, item)

    @staticmethod
    def _item_key(item):
        return item.id
