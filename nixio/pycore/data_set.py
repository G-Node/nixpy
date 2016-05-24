# Copyright (c) 2016, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.


class DataSet(object):

    def __init__(self):
        self.data_extent = None
        self.data_type = None

    def _write_data(self):
        pass

    def _read_data(self):
        pass

    def _get_dtype(self):
        pass


class DataView(DataSet):

    def __init__(self):
        super(DataView, self).__init__()
