// Copyright (c) 2014, German Neuroinformatics Node (G-Node)
//
// All rights reserved.
//
// Redistribution and use in source and binary forms, with or without
// modification, are permitted under the terms of the BSD License. See
// LICENSE file in the root of the Project.

#include <docstrings.hpp>

namespace nixpy {
namespace doc {

// PyEntity

const char* entity_id = R"(
A property providing the ID of the Entity. The id is generated automatically,
therefore the property is read-only.

:type: str
)";

const char* entity_crated_at = R"(
    The creation time of the entity. This is a read-only property. Use :py:meth:force_created_at in order to
    change the creation time.

    :type: int
    )";


const char* entity_force_created_at = R"(
    Sets the creation time created_at to the given time.

    :param time: The time to set
    :type time: int

    :rtype: None
    )";

const char* entity_updated_at = R"(
    The time of the last update of the entity. This is a read-only property. Use force_updated_at in order
    to change the update time.

    :type: int
    )";

const char* entity_force_updated_at = R"(
    Sets the update time updated_at to the current time.

    :rtype: None
    )";

// PyNamedEntity

const char* entity_name = R"(
    The name of an entity. The name serves as a human readable identifier.
    This is a read-write property, but it can't be set to None.

    :type: str
    )";

const char* entity_type = R"(
    The type of the entity. The type is used in order to add semantic meaning to the entity.
    This is a read-write property, but it can't be set to None.

    :type: str
    )";

const char* entity_definition = R"(
    The definition of the entity. The definition can contain a textual description of the
    entity. This is an optional read-write property, and can be None if no definition is available.

    :type: str
    )";

// PyEntityWithMetadata

const char* entity_metadata = R"(
    Associated metadata of the entity. Sections attached to the entity via this attribute can
    provide additional annotations. This is an optional read-write property, and can be None if
    no metadata is available.

    :type: Section
    )";

// PyFile

const char* file_version = R"(
    The file format version.

    :type: str
    )";

const char* file_format = R"(
    The format of the file. This read only property should have
    always the value 'nix'.

    :type: str
    )";

const char* file_create_block = R"(
    Create a new block inside the file.

    :param name: The name of the block to create.
    :type name: str
    :param type: The type of the block.
    :type type: str

    :returns: The newly created block.
    :rtype: Block
    )";

const char* file_create_section = R"(
    Create a new metadata section inside the file.

    :param name: The name of the section to create.
    :type name: str
    :param type: The type of the section.
    :type type: str

    :returns: The newly created section.
    :rtype: Section
    )";

const char* file_is_open = R"(
    Checks whether a file is open or closed.

    :returns: True if the file is open, False otherwise.
    :rtype: bool
    )";

const char* file_close = R"(
    Closes an open file.
    )";

const char* file_open = R"(
    Static method for opening a file.

    :param name: The path to the file to open.
    :type name: str
    :param open_mode: The open mode (default FileMode.ReadWrite)
    :type open_mode: FileMode

    :returns: The open file.
    :rtype: File
    )";

// PyBlock

const char* block_create_data_array = R"(
    Create a new data array for this block.

    :param name: The name of the data array to create.
    :type name: str
    :param type: The type of the data array.
    :type type: str

    :returns: The newly created data array.
    :rtype: DataArray
    )";

const char* block_create_simple_tag = R"(
    Create a new simple tag for this block.

    :param name: The name of the tag to create.
    :type name: str
    :param type: The type of tag.
    :type type: str
    :param references: All referenced data arrays.
    :type references: list

    :returns: The newly created tag.
    :rtype: SimpleTag
    )";

const char* block_create_data_tag = R"(
    Create a new simple tag for this block.

    :param name: The name of the tag to create.
    :type name: str
    :param type: The type of tag.
    :type type: str
    :param positions: A data array defining all positions of the tag.
    :type positions: DataArray

    :returns: The newly created tag.
    :rtype: DataTag
    )";

const char* block_create_source = R"(
    Create a new source on this block.

    :param name: The name of the source to create.
    :type name: str
    :param type: The type of the source.
    :type type: str

    :returns: The newly created source.
    :rtype: Source
    )";
}
}
