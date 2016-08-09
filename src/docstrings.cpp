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
    The format of the file. This read only property should always have
    the value 'nix'.

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
    :param position: Coordinates of the start position
                     in units of the respective data dimension.

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

const char* block_create_group = R"(
    Create a new group on this block.

    :param name: The name of the group to create.
    :type name: str
    :param type: The type of the group.
    :type type: str

    :returns: The newly created group.
    :rtype: Group
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
    The expansion origin of the calibration polynomial. This is a read-write
    property and can be set to None. The default value is 0.

    :type: float
    )";

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

const char* data_array_create_alias_range_dimension = R"(
    Append a new RangeDimension that uses the data stored in this DataArray as ticks.
    This works only(!) if the DataArray is 1-D and the stored data is numeric. A ValueError
    will be raised otherwise.

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

const char* data_array_append_alias_range_dimension = R"(
    Append a new RangeDimension that uses the data stored in this DataArray as ticks.
    This works only if the data is 1-D and numeric. That is, this dimension discriptor must be
    the only descriptor in this DataArray. An ValueError is raised otherwise.

    :returns: The newly created RangeDimension.
    :rtype: RangeDimension
    )";

// PyTag

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

// PyDimension

const char* sampled_dimension_axis = R"(
    Get an axis as defined by this sampled dimension.

    :param count: A positive integer specifying the length of the axis
    (no of samples).
    :param start: positive integer, indicates the starting sample.

    :returns: The created axis
    :rtype: list
    )";

const char* sampled_dimension_index_of = R"( 
    Returns the index of a certain position in the dimension.

    :param position: The position. 

    :returns: The nearest index.
    :rtype: int
    )";


const char* sampled_dimension_position_at = R"(
    Returns the position corresponding to a given index.

    :param index: A positive integer.

    :returns: The position matching to the index.
    :rtype: float
    )";


const char* range_dimension_index_of = R"(
    Returns the index of a certain position in the dimension.

    :param position: The position.

    :returns: The nearest index.
    :rtype: int
    )";


const char* range_dimension_tick_at = R"(
    Returns the tick at the given index. Will throw an Exception if the index is out of bounds.

    :param index: The index.

    :returns: The corresponding position.
    :rtype: double
    )";


const char* range_dimension_axis = R"(
    Get an axis as defined by this range dimension.

    :param count: A positive integer specifying the length of the axis
    (no of points).
    :param start: positive integer, indicates the starting tick.

    :returns: The created axis
    :rtype: list
    )";


// PyResult

const char* mesage_id = R"(
    The id of the element that caused the message.
    This is a read only property.

    :type: str
    )";

const char* message_msg = R"(
    The actual error or warning message.
    This is a read only property.

    :type: str
    )";

const char* result_errors = R"(
    A list of all error messages in this validation result.
    This is a read only property.

    :type: tuple of str
    )";

const char* result_warnings = R"(
    A list of all warning messages in this validation result.
    This is a read only property.

    :type: tuple of str
    )";

const char* result_is_ok = R"(
    The status of the validation result.

    :returns: True if the result contains no warnings or errors,
              False otherwise.
    :rtype: bool
    )";

const char* result_has_warnings = R"(
    The warning status of the validation result.

    :returns: True if the result contains warnings, False otherwise.
    :rtype: bool
    )";

const char* result_has_errors = R"(
    The error status of the validation result.

    :returns: True if the result contains warnings, False otherwise.
    :rtype: bool
    )";

// PyUtil

const char* unit_is_si = R"(
    Determines whether a unit is a recognized SI unit.

    :param unit: The unit that needs to be checked.

    :returns: True if the unit is an SI unit, false otherwise.
    :rtype: bool
    )";

const char* unit_sanitizer = R"(
    Sanitizes a unit string. That is, it is de-blanked, and mu and µ symbols are changed
    to u for micro.

    :param unit: The unit that needs to be sanitized.

    :returns: the sanitized unit.
    :rtype: str
    )";

const char* unit_is_atomic = R"(
    Checked whether a unit string represents an atomic si unit, i.e. not a
    combination.

    :param unit: The unit to be checked.

    :returns: True if unit is atomic, False otherwise.
    :rtype: bool
    )";

const char* unit_is_compound = R"(
    Checks whether a unit string represents a combination of SI units.

    :param unit: The unit string.

    :returns: True if the unit string represents a combination of SI units, False otherwise.
    :rtype: bool
    )";

const char* unit_split = R"(
    Splits a unit string into magnitude prefix, the base unit, and the power.

    :param unit: The unit string.

    :returns: A tuple of prefix, base unit, and power.
    :rtype: tuple
    )";

const char* unit_compound_split = R"(
    Splits a compound unit (like mV/Hz) into the atomic units.

    :param unit: The unit string.

    :returns: A tuple containing the atomic units.
    :rtype: tuple
    )";

const char* unit_scalable = R"(
    Checks whether units are scalable versions of the same SI unit. Method works on two lists and
    compares the corresponding units in both lists.

    :param units_1: List of unit strings.
    :param units_2: List of unit strings.

    :returns: True if all corresponding units are scalable.
    :rtype: bool
    )";

const char* unit_scaling = R"(
    Returns the scaling factor to convert from unit_1 to unit_2.

    :param unit_1: The unit string.
    :param unit_2: The unit string.

    :returns: The scaling factor.
    :rtype: double
    )";

const char* name_sanitizer = R"(
    Sanitizes a string supposed to be an entity name. That is,
    invalid characters like slashes are substituted with underscores.

    :param name: A string representing the name.

    :returns: The sanitized name.
    :rtype: str
    )";

const char* name_check = R"(
    Checks a string whether is needs to be sanitized.

    :param name: The name.

    :returns: True if the name is valid, false otherwise.
    :rtype: bool
    )";

const char* create_id = R"(
    Creates an ID as used for nix entities.

    :returns: The ID.
    :rtype: str
    )";

}
}
