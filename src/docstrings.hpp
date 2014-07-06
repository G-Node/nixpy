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

extern const char* block_create_simple_tag;

extern const char* block_create_data_tag;

extern const char* block_create_source;
}
}

#endif
