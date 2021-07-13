import importlib.util as getmod
import os
import runpy
import unittest

from pathlib import Path
from shutil import copyfile

import matplotlib.pyplot as plt


TEST_IMAGE = "lenna.png"


class TestDocumentationExamples(unittest.TestCase):

    def run_script(self, script_name):
        file_path = Path.joinpath(self.examples_path, script_name)
        runpy.run_path(path_name=str(file_path), run_name="__main__")

    def handle_lif(self):
        lif_path = Path.joinpath(self.examples_path, "lif.py")
        spec = getmod.spec_from_file_location("lif", str(lif_path))
        spec.loader.load_module("lif")

    def handle_image(self):
        image_path = Path.joinpath(self.examples_path, TEST_IMAGE)
        copyfile(str(image_path), str(Path.joinpath(Path(os.getcwd()), TEST_IMAGE)))

    def setUp(self):
        curr_path = os.getcwd()
        if os.path.basename(curr_path) == "nixpy":
            self.examples_path = Path.joinpath(Path(curr_path),
                                               "docs", "source", "examples")
        elif os.path.basename(curr_path) == "nixio":
            self.examples_path = Path.joinpath(Path(curr_path).parent,
                                               "docs", "source", "examples")
        elif os.path.basename(curr_path) == "test":
            self.examples_path = Path.joinpath(Path(curr_path).parent.parent,
                                               "docs", "source", "examples")

        # Render matplotlib plots non-blocking
        plt.ion()

    def tearDown(self):
        plt.close("all")
        plt.ioff()
        if os.path.exists(TEST_IMAGE):
            os.remove(TEST_IMAGE)

    def test_annotations(self):
        self.run_script("annotations.py")
        # cleanup
        os.remove("annotations.nix")

    def test_category_data(self):
        self.run_script("categoryData.py")
        # cleanup
        os.remove("categoryData.nix")

    def test_continuous_recording(self):
        self.run_script("continuousRecording.py")
        # cleanup
        os.remove("continuous_recording.nix")

    def test_file_create(self):
        self.run_script("fileCreate.py")
        # cleanup
        os.remove("file_create_example.nix")

    def test_image_data(self):
        # Requires PIL package and the "Lenna" image.
        self.handle_image()
        self.run_script("imageData.py")
        # cleanup
        os.remove("image_example.nix")

    def test_image_with_metadata(self):
        # Requires PIL package and the "Lenna" image.
        self.handle_image()
        self.run_script("imageWithMetadata.py")
        # cleanup
        os.remove("image_with_source_example.h5")
        os.remove("image_with_metadata.png")

    def test_irregularly_sampled_data(self):
        self.run_script("irregularlySampledData.py")
        # cleanup
        os.remove("irregular_data_example.nix")

    def test_lif(self):
        self.run_script("lif.py")

    def test_multiple_points(self):
        self.run_script("multiple_points.py")
        # cleanup
        os.remove("multiple_points.nix")

    def test_multiple_regions(self):
        self.run_script("multiple_regions.py")
        # cleanup
        os.remove("multiple_regions.nix")

    def test_multiple_rois(self):
        # Requires PIL package and the "Lenna" image.
        self.handle_image()
        self.run_script("multipleROIs.py")
        # cleanup
        os.remove("multiple_roi.nix")

    def test_range_dimension_link(self):
        self.run_script("rangeDimensionLink.py")
        # cleanup
        os.remove("range_link.nix")

    def test_regularly_sampled_data(self):
        self.run_script("regularlySampledData.py")
        # cleanup
        os.remove("regular_data_example.nix")

    def test_single_roi(self):
        # Requires PIL package and the "Lenna" image.
        self.handle_image()
        self.run_script("singleROI.py")
        # cleanup
        os.remove("single_roi.nix")

    def test_sources(self):
        self.run_script("sources.py")
        # cleanup
        os.remove("sources.nix")

    def test_spike_features(self):
        # Requires scipy package and "lif.py"
        self.handle_lif()
        self.run_script("spikeFeatures.py")
        # cleanup
        os.remove("spike_features.h5")

    def test_spike_tagging(self):
        # Requires "lif.py"
        self.handle_lif()
        self.run_script("spikeTagging.py")
        # cleanup
        os.remove("spike_tagging.nix")

    def test_tabular_data(self):
        self.run_script("tabulardata.py")
        # cleanup
        os.remove("dataframe.nix")

    def test_tagged_feature(self):
        # Requires scipy package and "lif.py"
        self.handle_lif()
        self.run_script("taggedFeature.py")
        # cleanup
        os.remove("spike_features.nix")

    def test_tagging_example(self):
        # Requires scipy package
        self.run_script("tagging_example.py")
        # cleanup
        os.remove("tagging1.nix")

    def test_tagging_nd(self):
        # not testing any nix feature
        # self.run_script("tagging_nd.py")
        pass

    def test_untagged_feature(self):
        # Requires scipy package and "lif.py"
        self.handle_lif()
        self.run_script("untaggedFeature.py")
        # cleanup
        os.remove("untagged_feature.h5")
