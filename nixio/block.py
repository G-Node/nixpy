# -*- coding: utf-8 -*-
# Copyright © 2014, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

try:
    from sys import maxint
except ImportError:
    from sys import maxsize as maxint
import numpy as np
from inspect import isclass
from six import string_types
try:
    from collections.abc import OrderedDict
except ImportError:
    from collections import OrderedDict
import sys

from .util import find as finders
from .compression import Compression

from .entity import Entity
from .exceptions import exceptions
from .group import Group
from .data_array import DataArray
from .data_frame import DataFrame
from .multi_tag import MultiTag
from .tag import Tag
from .source import Source
from . import util
from .container import Container, SourceContainer
from .section import Section


class Block(Entity):

    def __init__(self, nixfile, nixparent, h5group,
                 compression=Compression.Auto):
        super(Block, self).__init__(nixfile, nixparent, h5group)
        self._groups = None
        self._data_arrays = None
        self._tags = None
        self._multi_tags = None
        self._sources = None
        self._compr = compression
        self._data_frames = None

    @classmethod
    def create_new(cls, nixparent, h5parent, name, type_, compression):
        nixfile = nixparent  # file is parent
        newentity = super(Block, cls).create_new(nixfile, nixparent, h5parent,
                                                 name, type_)
        newentity._compr = compression
        return newentity

    # MultiTag
    def create_multi_tag(self, name="", type_="", positions=None,
                         extents=None, copy_from=None, keep_copy_id=True):
        """
        Create/copy a new multi tag for this block.

        :param name: The name of the tag to create/copy.
        :type name: str
        :param type_: The type of tag.
        :type type_: str
        :param positions: A data array defining all positions of the tag.
        :type positions: DataArray
        :param copy_from: The MultiTag to be copied, None in normal mode
        :type copy_from: MultiTag
        :param keep_copy_id: Specify if the id should be copied in copy mode
        :type keep_copy_id: bool

        :returns: The newly created tag.
        :rtype: MultiTag
        """
        if copy_from:
            if not isinstance(copy_from, MultiTag):
                raise TypeError("Object to be copied is not a MultiTag")
            id = self._copy_objects(copy_from, "multi_tags",
                                    keep_copy_id, name)
            return self.multi_tags[id]

        util.check_entity_name_and_type(name, type_)
        multi_tags = self._h5group.open_group("multi_tags")
        if name in multi_tags:
            raise exceptions.DuplicateName("create_multi_tag")
        poscreated = False
        extcreated = False
        try:
            if not isinstance(positions, DataArray):
                da_name = "{}-positions".format(name)
                positions = self.create_data_array(
                    da_name, "{}-positions".format(type_), data=positions
                )
                poscreated = True
            if not isinstance(extents, DataArray) and extents is not None:
                da_name = "{}-extents".format(name)
                extents = self.create_data_array(da_name,
                                                 "{}-extents".format(type_),
                                                 data=extents)
                extcreated = True
            mtag = MultiTag.create_new(self.file, self, multi_tags,
                                       name, type_, positions)
        except Exception as e:
            msg = "MultiTag Creation Failed"
            if poscreated:
                del self.data_arrays["{}-positions".format(name)]
            else:
                msg += " due to invalid positions"
            if extcreated:
                del self.data_arrays["{}-extents".format(name)]
            elif poscreated and not extcreated:
                msg += " due to invalid extents"
            print(msg)
            raise e

        if extents is not None:
            mtag.extents = extents
        return mtag

    # Tag
    def create_tag(self, name="", type_="", position=0,
                   copy_from=None, keep_copy_id=True):
        """
        Create/copy a new tag for this block.

        :param name: The name of the tag to create/copy.
        :type name: str
        :param type_: The type of tag.
        :type type_: str
        :param position: Coordinates of the start position
                         in units of the respective data dimension.
        :param copy_from: The Tag to be copied, None in normal mode
        :type copy_from: Tag
        :param keep_copy_id: Specify if the id should be copied in copy mode
        :type keep_copy_id: bool

        :returns: The newly created tag.
        :rtype: Tag
        """
        if copy_from:
            if not isinstance(copy_from, Tag):
                raise TypeError("Object to be copied is not a Tag")
            id = self._copy_objects(copy_from, "tags", keep_copy_id, name)
            return self.tags[id]

        util.check_entity_name_and_type(name, type_)
        tags = self._h5group.open_group("tags")
        if name in tags:
            raise exceptions.DuplicateName("create_tag")
        tag = Tag.create_new(self.file, self, tags, name, type_, position)
        return tag

    # Source
    def create_source(self, name, type_):
        """
        Create a new source on this block.

        :param name: The name of the source to create.
        :type name: str
        :param type_: The type of the source.
        :type type_: str

        :returns: The newly created source.
        :rtype: Source
        """
        util.check_entity_name_and_type(name, type_)
        sources = self._h5group.open_group("sources")
        if name in sources:
            raise exceptions.DuplicateName("create_source")
        src = Source.create_new(self.file, self, sources, name, type_)
        return src

    # Group
    def create_group(self, name, type_):
        """
        Create a new group on this block.

        :param name: The name of the group to create.
        :type name: str
        :param type_: The type of the group.
        :type type_: str

        :returns: The newly created group.
        :rtype: Group
        """
        util.check_entity_name_and_type(name, type_)
        groups = self._h5group.open_group("groups")
        if name in groups:
            raise exceptions.DuplicateName("open_group")
        grp = Group.create_new(self.file, self, groups, name, type_)
        return grp

    def create_data_array(self, name="", array_type="", dtype=None, shape=None,
                          data=None, compression=Compression.Auto,
                          copy_from=None, keep_copy_id=True):
        """
        Create/copy a new data array for this block. Either ``shape``
        or ``data`` must be given. If both are given their shape must agree.
        If ``dtype`` is not specified it will default to 64-bit floating
        points.

        :param name: The name of the data array to create/copy.
        :type name: str
        :param array_type: The type of the data array.
        :type array_type: str
        :param dtype: Which data-type to use for storage
        :type dtype:  :class:`numpy.dtype`
        :param shape: Layout (dimensionality and extent)
        :type shape: tuple of int or long
        :param data: Data to write after storage has been created
        :type data: array-like data
        :param compression: En-/disable dataset compression.
        :type compression: :class:`~nixio.Compression`
        :param copy_from: The DataArray to be copied, None in normal mode
        :type copy_from: DataArray
        :param keep_copy_id: Specify if the id should be copied in copy mode
        :type keep_copy_id: bool

        :returns: The newly created data array.
        :rtype: :class:`~nixio.DataArray`
        """

        if copy_from:
            if not isinstance(copy_from, DataArray):
                raise TypeError("Object to be copied is not a DataArray")
            id = self._copy_objects(copy_from, "data_arrays",
                                    keep_copy_id, name)
            return self.data_arrays[id]

        if data is None:
            if shape is None:
                raise ValueError("Either shape and or data must not be None")
            if dtype is None:
                dtype = 'f8'
        else:
            data = np.ascontiguousarray(data)
            if dtype is None:
                dtype = data.dtype
            if shape is not None:
                if shape != data.shape:
                    raise ValueError("Shape must equal data.shape")
            else:
                shape = data.shape
        util.check_entity_name_and_type(name, array_type)
        data_arrays = self._h5group.open_group("data_arrays")
        if name in data_arrays:
            raise exceptions.DuplicateName("create_data_array")
        if compression == Compression.Auto:
            compression = self._compr
        da = DataArray.create_new(self.file, self, data_arrays, name, array_type,
                                  dtype, shape, compression)
        if data is not None:
            da.write_direct(data)
        return da

    def create_data_frame(self, name="", type_="", col_dict=None,
                          col_names=None, col_dtypes=None, data=None,
                          compression=Compression.No,
                          copy_from=None, keep_copy_id=True):
        """
        Create/copy a new data frame for this block. Either ``col_dict``
        or ``col_name`` and ``col_dtypes`` must be given.
        If both are given, ``col_dict`` will be used.

        :param name: The name of the data frame to create/copy.
        :type name: str
        :param type_: The type of the data frame.
        :type type_: str
        :param col_dict: The dictionary that specifies column
                         names and data type in each column
        :type col_dict: dict or OrderedDict of {str: type}
        :param col_names: The collection of name of all columns in order
        :type col_names: tuples or list or np.array of string
        :param col_dtypes: The collection of data type of all columns in order
        :type col_dtypes: tuples or list or np.array of type
        :param data: Data to write after storage has been created
        :type data: array-like data with compound data type
                    as specified in the columns
        :param compression: En-/disable dataset compression.
        :type compression: :class:`~nixio.Compression`
        :param copy_from: The DataFrame to be copied, None in normal mode
        :type copy_from: DataFrame
        :param keep_copy_id: Specify if the id should be copied in copy mode
        :type keep_copy_id: bool

        :returns: The newly created data frame.
        :rtype: :class:`~nixio.DataFrame`
        """
        if copy_from:
            if not isinstance(copy_from, DataFrame):
                raise TypeError("Object to be copied is not a DataFrame")
            id = self._copy_objects(copy_from, "data_frames",
                                    keep_copy_id, name)
            return self.data_frames[id]

        util.check_entity_name_and_type(name, type_)
        if (isinstance(col_dict, dict)
                and not isinstance(col_dict, OrderedDict)
                and sys.version_info[0] < 3):
            raise TypeError("Python 2 users should use name_list "
                            "or OrderedDict created with LIST and TUPLES "
                            "to create DataFrames as the order "
                            "of the columns cannot be maintained in Py2")

        if data is not None:
            shape = len(data)
        else:
            shape = 0
        data_frames = self._h5group.open_group("data_frames")

        if col_dict is None:
            if col_names is not None:
                if col_dtypes is not None:
                    col_dict = OrderedDict(
                        (str(nam), dt)
                        for nam, dt in zip(col_names, col_dtypes)
                    )
                elif col_dtypes is None and data is not None:
                    col_dtypes = []
                    for x in data[0]:
                        col_dtypes.append(type(x))
                    col_dict = OrderedDict(
                        (str(nam), dt)
                        for nam, dt in zip(col_names, col_dtypes)
                    )
                else:  # col_dtypes is None and data is None
                    raise ValueError(
                        "The data type of each column have to be specified"
                    )
                if len(col_names) != len(col_dict):
                    raise exceptions.DuplicateColumnName
            else:  # if col_names is None
                if data is not None and type(data[0]) == np.void:
                    col_dtype = data[0].dtype
                    for i, dt in enumerate(col_dtype.fields.values()):
                        cn = list(col_dtype.fields.keys())
                        raw_dt = col_dtype.fields.values()
                        raw_dt = list(raw_dt)
                        raw_dt_list = [ele[0] for ele in raw_dt]
                    col_dict = OrderedDict(zip(cn, raw_dt_list))
                    if len(col_dtype.fields.values()) != len(col_dict):
                        raise exceptions.DuplicateColumnName

                else:
                    # data is None or type(data[0]) != np.void
                    # data_type doesnt matter
                    raise ValueError(
                        "No information about column names is provided!"
                    )

        if col_dict is not None:
            for nam, dt in col_dict.items():
                if isclass(dt):
                    if any(issubclass(dt, st) for st in string_types) \
                            or issubclass(dt, np.string_):
                        col_dict[nam] = util.vlen_str_dtype
                if 'U' in str(dt) or dt == np.string_:
                    col_dict[nam] = util.vlen_str_dtype
            dt_arr = list(col_dict.items())
            col_dtype = np.dtype(dt_arr)

        df = DataFrame.create_new(self.file, self, data_frames, name,
                                  type_, shape, col_dtype, compression)

        if data is not None:
            if type(data[0]) == np.void:
                data = np.ascontiguousarray(data, dtype=col_dtype)
                df.write_direct(data)
            else:
                data = list(map(tuple, data))
                arr = np.ascontiguousarray(data, dtype=col_dtype)
                df.write_direct(arr)
        return df

    def find_sources(self, filtr=lambda _: True, limit=None):
        """
        Get all sources in this block recursively.

        This method traverses the tree of all sources in the block. The
        traversal is accomplished via breadth first and can be limited in
        depth.  On each node or source a filter is applied. If the filter
        returns true the respective source will be added to the result list.
        By default a filter is used that accepts all sources.

        :param filtr: A filter function
        :type filtr:  function
        :param limit: The maximum depth of traversal
        :type limit:  int

        :returns: A list containing the matching sources.
        :rtype: list of Source
        """
        if limit is None:
            limit = maxint
        return finders._find_sources(self, filtr, limit)

    def pprint(self, indent=2, max_length=120, extra=True, start_depth=0):
        """
        Pretty Printing the Data and MetaData Tree of the whole File

        :param indent: The length of one indentation space
        :type indent: int
        :param max_length: Maximum length of each line of output
        :type max_length: int
        :param extra: True to print extra information of Entities
        :type extra: bool
        :param start_depth: Starting depth of indentation
        :type start_depth: int
        """
        print("{}{}".format(" " * indent*start_depth, self))
        for grp in self.groups:
            self._pp(grp, max_length, indent*(start_depth + 1), False)
            for da in grp.data_arrays:
                self._pp(da, max_length, indent*(start_depth + 2),
                         extra, True)
                for dim in da.dimensions:
                    self._pp(dim, max_length, indent*(start_depth + 3), False)
            for df in grp.data_frames:
                self._pp(df, max_length,
                         indent*(start_depth + 2), extra, True)
            for tag in grp.tags:
                self._pp(tag, max_length,
                         indent*(start_depth + 2), extra, True)
                for fe in tag.features:
                    self._pp(fe, max_length, indent*(start_depth + 3), False)
            for mt in grp.multi_tags:
                self._pp(mt, max_length, indent*(start_depth + 2), extra, True)
                for fe in mt.features:
                    self._pp(fe, max_length, indent*(start_depth + 3), False)
        for da in self.data_arrays:
            self._pp(da, max_length, indent*(start_depth + 1), extra)
            for dim in da.dimensions:
                self._pp(dim, max_length, indent*(start_depth + 2), False)
        for df in self.data_frames:
            self._pp(df, max_length, indent*(start_depth + 1), extra)
        for tag in self.tags:
            self._pp(tag, max_length, indent*(start_depth + 1), extra)
            for fe in tag.features:
                self._pp(fe, max_length, indent*(start_depth + 2), False)
        for mt in self.multi_tags:
            self._pp(mt, max_length, indent*(start_depth + 1), extra)
            for fe in mt.features:
                self._pp(fe, max_length, indent*(start_depth + 2), False)

    @staticmethod
    def _pp(obj, ml, indent, ex, grp=False):
        spaces = " "*(indent)
        if grp:
            prefix = "*"
        else:
            prefix = ""
        if ex:
            stat = ""
            if isinstance(obj, MultiTag):
                stat = "Position Shape:{} Units: {}".format(
                    obj.positions.shape,
                    obj.units)
            elif isinstance(obj, Tag):
                stat = "Position Length:{} Units: {}".format(len(obj.position),
                                                             obj.units)
            elif isinstance(obj, DataFrame):
                stat = "Shape: {} Columns:{}".format(obj.shape,
                                                     obj.column_names)
            elif isinstance(obj, DataArray):
                stat = "Shape: {} Unit:{}".format(obj.shape, obj.unit)
            p = "{}{}{}".format(spaces, prefix, obj)
            n = "{}  {}".format(spaces, stat)
        else:
            p = "{}{}{}".format(spaces, prefix, obj)
        if len(p) > ml - 4:
            split_len = int(ml/2)
            str1 = p[0:split_len]
            str2 = p[-split_len:]
            print("{} ... {}".format(str1, str2))
        else:
            print(p)
        if ex:
            if len(n) > ml - 4:
                split_len = int(ml/2)
                nstr1 = n[0:split_len]
                nstr2 = n[-split_len:]
                print("{} ... {}".format(nstr1, nstr2))
            else:
                print(n)

    def _copy_objects(self, obj, clsname, keep_id=True, name=""):
        src = "{}/{}".format(clsname, obj.name)
        if not name:
            name = str(obj.name)
        ogrp = self._h5group.open_group(clsname, True)
        if name in ogrp:
            raise NameError("Name already exist. Possible solution is to "
                            "provide a new name when copying destination "
                            "is the same as the source parent")
        o = obj._parent._h5group.copy(source=src, dest=self._h5group,
                                      name=name, cls=clsname,
                                      keep_id=keep_id)

        return o.attrs["entity_id"]

    @property
    def sources(self):
        """
        A property containing all sources of a block. Sources can be obtained
        via their index or by their id. Sources can be deleted from the list.
        Adding sources is done using the Blocks create_source method.
        This is a read only attribute.
        """
        if self._sources is None:
            self._sources = SourceContainer("sources", self.file, self, Source)
        return self._sources

    @property
    def multi_tags(self):
        """
        A property containing all multi tags of a block. MultiTag entities can
        be obtained via their index or by their id. Tags can be deleted from
        the list. Adding tags is done using the Blocks create_multi_tag method.
        This is a read only attribute.
        """
        if self._multi_tags is None:
            self._multi_tags = Container("multi_tags", self.file,
                                         self, MultiTag)
        return self._multi_tags

    @property
    def tags(self):
        """
        A property containing all tags of a block. Tag entities can be obtained
        via their index or by their id. Tags can be deleted from the list.
        Adding tags is done using the Blocks create_tag method.
        This is a read only attribute.
        """
        if self._tags is None:
            self._tags = Container("tags", self.file, self, Tag)
        return self._tags

    @property
    def data_arrays(self):
        """
        A property containing all data arrays of a block. DataArray entities
        can be obtained via their index or by their id. Data arrays can be
        deleted from the list. Adding a data array is done using the Blocks
        create_data_array method.
        This is a read only attribute.
        """
        if self._data_arrays is None:
            self._data_arrays = Container("data_arrays", self.file,
                                          self, DataArray)
        return self._data_arrays

    @property
    def data_frames(self):
        if self._data_frames is None:
            self._data_frames = Container("data_frames", self.file,
                                          self, DataFrame)
        return self._data_frames

    @property
    def groups(self):
        """
        A property containing all groups of a block. Group entities can be
        obtained via their index or by their id. Groups can be deleted from the
        list. Adding a Group is done using the Blocks create_group method.
        This is a read only attribute.
        """
        if self._groups is None:
            self._groups = Container("groups", self.file, self, Group)
        return self._groups

    # metadata
    @property
    def metadata(self):
        """
        Associated metadata of the entity. Sections attached to the entity via
        this attribute can provide additional annotations. This is an optional
        read-write property, and can be None if no metadata is available.

        :type: Section
        """
        if "metadata" in self._h5group:
            return Section(self.file, None,
                           self._h5group.open_group("metadata"))
        else:
            return None

    @metadata.setter
    def metadata(self, sect):
        if not isinstance(sect, Section):
            raise TypeError("{} is not of type Section".format(sect))
        self._h5group.create_link(sect, "metadata")

    @metadata.deleter
    def metadata(self):
        if "metadata" in self._h5group:
            self._h5group.delete("metadata")
