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

extern const char* entity_id;

extern const char* entity_crated_at;


extern const char* entity_force_created_at;

extern const char* entity_updated_at;

extern const char* entity_force_updated_at;

// PyNamedEntity

extern const char* entity_name;

extern const char* entity_type;

extern const char* entity_definition;

// PyEntityWithMetadata

extern const char* entity_metadata;

// PyFile

extern const char* file_version;

extern const char* file_format;

extern const char* file_create_block;

extern const char* file_create_section;

extern const char* file_is_open;

extern const char* file_close;

extern const char* file_open;

// PyBlock

extern const char* block_create_data_array;

extern const char* block_create_tag;

extern const char* block_create_multi_tag;

extern const char* block_create_source;

// PySection

extern const char* section_repository;

extern const char* section_mapping;

extern const char* section_link;

extern const char* section_parent;

extern const char* section_create_section;

extern const char* section_create_property;

extern const char* section_has_property_by_name;

extern const char* section_get_property_by_name;

// PyDataArray

extern const char* data_array_label;

extern const char* data_array_unit;

extern const char* data_array_expansion_origin;

extern const char* data_array_polynom_coefficients;

extern const char* data_array_data_extent;

extern const char* data_array_data_type;

extern const char* data_array_create_set_dimension;

extern const char* data_array_create_sampled_dimension;

extern const char* data_array_create_range_dimension;

extern const char* data_array_append_set_dimension;

extern const char* data_array_append_sampled_dimension;

extern const char* data_array_append_range_dimension;

// PyTag

extern const char* tag_units;

extern const char* tag_position;

extern const char* tag_extent;

extern const char* tag_create_feature;

// PyMultiTag

extern const char* multi_tag_units;

extern const char* multi_tag_positions;

extern const char* multi_tag_extents;

extern const char* multi_tag_create_feature;

// PyDimension

extern const char* sampled_dimension_axis;

extern const char* sampled_dimension_position_at;

extern const char* sampled_dimension_index_of;

// PyResult

extern const char* mesage_id;

extern const char* message_msg;

extern const char* result_errors;

extern const char* result_warnings;

extern const char* result_is_ok;

extern const char* result_has_warnings;

extern const char* result_has_errors;

}
}

#endif
