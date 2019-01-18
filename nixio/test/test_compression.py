# -*- coding: utf-8 -*-
# Copyright © 2017, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in section and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.
import os
import nixio as nix
import unittest
from .tmp import TempDir


def compr_enabled(da):
    grp = da._h5group.group
    h5data = grp.require_dataset("data", shape=(1,), dtype=int)
    return h5data.compression == "gzip"


class TestCompression(unittest.TestCase):

    def setUp(self):
        self.tmpdir = TempDir("compressiontest")
        self.testfilename = os.path.join(self.tmpdir.path,
                                         "compressiontest.nix")

    def tearDown(self):
        pass

    def test_compress_dataarray(self):

        exception = ValueError("Unknown compression value in test")
        for filecompr in nix.Compression:
            nf = nix.File.open(self.testfilename, nix.FileMode.Overwrite,
                               compression=filecompr)
            for blockcompr in nix.Compression:
                block = nf.create_block("block-{}".format(blockcompr),
                                        "block", compression=blockcompr)
                for dacompr in nix.Compression:
                    da = block.create_data_array("da-{}".format(dacompr),
                                                 "data", data=[0],
                                                 compression=dacompr)

                    if dacompr == nix.Compression.No:
                        comprenabled = False
                    elif dacompr == nix.Compression.DeflateNormal:
                        comprenabled = True
                    elif dacompr == nix.Compression.Auto:
                        # inherited from Block setting
                        if blockcompr == nix.Compression.No:
                            comprenabled = False
                        elif blockcompr == nix.Compression.DeflateNormal:
                            comprenabled = True
                        elif blockcompr == nix.Compression.Auto:
                            # inherited from File setting
                            if filecompr == nix.Compression.No:
                                comprenabled = False
                            elif filecompr == nix.Compression.DeflateNormal:
                                comprenabled = True
                            elif filecompr == nix.Compression.Auto:
                                comprenabled = False
                            else:
                                raise exception
                        else:
                            raise exception
                    else:
                        raise exception

                    errmsg = ("Compression: File [{}] Block [{}] Data [{}] "
                              "Expected compression {}".format(
                                  filecompr, blockcompr, dacompr, comprenabled
                              ))
                    self.assertEqual(compr_enabled(da), comprenabled, errmsg)
            nf.close()
