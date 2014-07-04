// Copyright (c) 2014, German Neuroinformatics Node (G-Node)
//
// All rights reserved.
//
// Redistribution and use in source and binary forms, with or without
// modification, are permitted under the terms of the BSD License. See
// LICENSE file in the root of the Project.

#ifndef NIXPY_DOCSTRINGS_H
#define NIXPY_DOCSTRINGS_H


namespace nixpy {
namespace doc {

// PyEntity

static const char* entity_id = R"(
    A property providing the ID of the Entity. The id is generated automatically,
    therefore the property is read-only.

    :type: str
    )";

static const char* entity_crated_at = R"(
    The creation time of the entity. This is a read-only property. Use :py:meth:force_created_at in order to
    change the creation time.

    :type: int
    )";


static const char* entity_force_created_at = R"(
    Sets the creation time created_at to the given time.

    :param time: The time to set
    :type time: int

    :rtype: None
    )";

static const char* entity_updated_at = R"(
    The time of the last update of the entity. This is a read-only property. Use force_updated_at in order
    to change the update time.

    :type: int
    )";

static const char* entity_force_updated_at = R"(
    Sets the update time updated_at to the current time.

    :rtype: None
    )";

// PyNamedEntity

static const char* entity_name = R"(
    The name of an entity. The name serves as a human readable identifier.
    This is a read-write property, but it can't be set to None.

    :type: str
    )";

static const char* entity_type = R"(
    The type of the entity. The type is used in order to add semantic meaning to the entity.
    This is a read-write property, but it can't be set to None.

    :type: str
    )";

static const char* entity_definition = R"(
    The definition of the entity. The definition can contain a textual description of the
    entity. This is an optional read-write property, and can be None if no definition is available.

    :type: str
    )";

// PyEntityWithMetadata

static const char* entity_metadata = R"(
    Associated metadata of the entity. Sections attached to the entity via this attribute can
    provide additional annotations. This is an optional read-write property, and can be None if
    no metadata is available.

    :type: Section
)";

// PyBlock

static const char* block_create_data_array = R"(
    Create a new data array for this block.

    :param name: The name of the data array to create.
    :type name: str
    :param type: The type of the data array.
    :type type: str

    :returns: The newly created data array.
    :rtype: DataArray
    )";

static const char* block_create_simple_tag = R"(
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

static const char* block_create_data_tag = R"(
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

static const char* block_create_source = R"(
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

#endif
