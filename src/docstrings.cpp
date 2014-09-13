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

// PySection

const char* section_repository = R"(
    URL to the terminology repository the section is associated with.
    This is an optional read-write property and may be set to None.

    :type: str
    )";

const char* section_mapping = R"(
    The mapping information of the section.
    This is an optional read-write property and may be set to None.

    :type: str
    )";

const char* section_link = R"(
    Link to another section. If a section is linked to another section, the
    linking section inherits all properties from the target section.
    This is an optional read-write property and may be set to None.

    :type: Section
    )";

const char* section_parent = R"(
    The parent section. This is a read-only property. For root sections
    this property is always None.

    :type: Section
    )";

const char* section_create_section = R"(
    Creates a new subsection that is a child of this section entity.

    :param name: The name of the section to create.
    :type name: str
    :param type: The type of the section.
    :type type: str

    :returns: The newly created section.
    :rtype: Section
    )";

const char* section_create_property = R"(
    Add a new property to the section.

    :param name: The name of the property to create.
    :type name: str
    :param values: The values of the property.
    :type values: list of Value

    :returns: The newly created property.
    :rtype: Property
    )";

const char* section_has_property_by_name = R"(
    Checks whether a section has a property with a certain name.

    :param name: The name to check.
    :type name: str

    :returns: True if the section has a property with the given name,
              False otherwise.
    :rtype: bool
    )";

const char* section_get_property_by_name = R"(
    Get a property by its name.

    :param name: The name to check.
    :type name: str

    :returns: The property with the given name.
    :rtype: Property
    )";

// PyBlock

const char* block_create_tag = R"(
    Create a new tag for this block.

    :param name: The name of the tag to create.
    :type name: str
    :param type: The type of tag.
    :type type: str
    :param references: All referenced data arrays.
    :type references: list

    :returns: The newly created tag.
    :rtype: Tag
    )";

const char* block_create_multi_tag = R"(
    Create a new multi tag for this block.

    :param name: The name of the tag to create.
    :type name: str
    :param type: The type of tag.
    :type type: str
    :param positions: A data array defining all positions of the tag.
    :type positions: DataArray

    :returns: The newly created tag.
    :rtype: MultiTag
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

// PyDataArray

const char* data_array_label = R"(
    The label of the DataArray. The label corresponds to the label of the
    x-axis of a plot. This is a read-write property and can be set to None.

    :type: str
    )";

const char* data_array_unit = R"(
    The unit of the values stored in the DataArray. This is a read-write property
    and can be set to None.

    :type: str
    )";

const char* data_array_expansion_origin = R"(
    The expansion origin of the calibration polynom. This is a read-write
    property and can be set to None. The default value is 0.

    :type: float)";

const char* data_array_polynom_coefficients = R"(
    The polynom coefficients for the calibration. By default this is set
    to a {0.0, 1.0} for a linear calibration with zero offset. This is a
    read-write property and can be set to None

    :type: list of float
    )";

const char* data_array_data_extent = R"(
    The size of the data.

    :type: set of int
    )";

const char* data_array_data_type = R"(
    The data type of the data stored in the DataArray. This is a read only
    property.

    :type: DataType
    )";

const char* data_array_create_set_dimension = R"(
    Create a new SetDimension at a specified dimension index. This adds a new
    dimension descriptor of the type SetDimension that describes the dimension
    of the data at the specified index.

    :param index: The index of the dimension. Must be a value > 0 and <=
                  len(dimensions) + 1.
    :type index: int

    :returns: The created dimension descriptor.
    :rtype: SetDimension
    )";

const char* data_array_create_sampled_dimension = R"(
    Create a new SampledDimension at a specified dimension index. This adds a
    new dimension descriptor of the type SampledDimension that describes the
    dimension of the data at the specified index.

    :param index: The index of the dimension. Must be a value > 0 and <=
                  len(dimensions) + 1.
    :type index: int
    :param sampling_interval:  The sampling interval of the dimension.
    :type sampling_interval: float

    :returns: The created dimension descriptor.
    :rtype: SampledDimension
    )";

const char* data_array_create_range_dimension = R"(
    Create a new RangeDimension at a specified dimension index. This adds a
    new dimension descriptor of the type RangeDimension that describes the
    dimension of the data at the specified index.

    :param index: The index of the dimension. Must be a value > 0 and <=
                  len(dimensions) + 1.
    :type index: int
    :param ticks: The ticks of the RangeDimension.
    :type ticks: list of float

    :returns: The created dimension descriptor.
    :rtype: RangeDimension
    )";

const char* data_array_append_set_dimension = R"(
    Append a new SetDimension to the list of existing dimension descriptors.

    :returns: The newly created SetDimension.
    :rtype: SetDimension
    )";

const char* data_array_append_sampled_dimension = R"(
    Append a new SampledDimension to the list of existing dimension
    descriptors.

    :param sampling_interval: The sampling interval of the SetDimension
                              to create.
    :type sampling_interval: float

    :returns: The newly created SampledDimension.
    :rtype: SampledDimension
    )";

const char* data_array_append_range_dimension = R"(
    Append a new RangeDimension to the list of existing dimension descriptors.

    :param ticks: The ticks of the RangeDimension to create.
    :type ticks: list of float

    :returns: The newly created RangeDimension.
    :rtype: RangeDimension
    )";


const char* tag_units = R"(
    Property containing the units of the tag. The tag must provide a unit for each
    dimension of the position or extent vector. This is a read-write property.

    :type: list of str
    )";

const char* tag_position = R"(
    The position defined by the tag. This is a read-write property.

    :type: list of float
    )";

const char* tag_extent = R"(
    The extent defined by the tag. This is an optional read-write property and may be set
    to None.

    :type: list of float
    )";

const char* tag_create_feature = R"(
    Create a new feature.

    :param data: The data array of this feature.
    :type data: DataArray
    :param link_type: The link type of this feature.
    :type link_type: LinkType

    :returns: The created feature object.
    :rtype: Feature
    )";

const char* multi_tag_units = R"(
    Property containing the units of the tag. The tag must provide a unit for each
    dimension of the positions or extents vector. This is a read-write property.

    :type: list of str
    )";

const char* multi_tag_positions = R"(
    The positions defined by the tag. This is a read-write property.

    :type: DataArray
    )";

const char* multi_tag_extents = R"(
    The extents defined by the tag. This is an optional read-write property and may be set
    to None.

    :type: DataArray or None
    )";

const char* multi_tag_create_feature = R"(
    Create a new feature.

    :param data: The data array of this feature.
    :type data: DataArray
    :param link_type: The link type of this feature.
    :type link_type: LinkType

    :returns: The created feature object.
    :rtype: Feature
    )";

}
}
