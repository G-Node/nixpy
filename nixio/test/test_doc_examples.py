import importlib.util as getmod
import matplotlib.pyplot as plt
import os
import runpy
import unittest

from pathlib import Path
from shutil import copyfile


class TestDocumentationExamples(unittest.TestCase):

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

    def test_annotations(self):
        file_path = Path.joinpath(self.examples_path, "annotations.py")
        runpy.run_path(path_name=str(file_path), run_name="__main__")
        # cleanup
        os.remove("annotations.nix")

    def test_category_data(self):
        file_path = Path.joinpath(self.examples_path, "categoryData.py")
        runpy.run_path(path_name=str(file_path), run_name="__main__")
        # cleanup
        os.remove("categoryData.nix")

    def test_continuous_recording(self):
        file_path = Path.joinpath(self.examples_path, "continuousRecording.py")
        runpy.run_path(path_name=str(file_path), run_name="__main__")
        # cleanup
        os.remove("continuous_recording.nix")

    def test_file_create(self):
        file_path = Path.joinpath(self.examples_path, "fileCreate.py")
        runpy.run_path(path_name=str(file_path), run_name="__main__")
        # cleanup
        os.remove("file_create_example.nix")

    def test_image_data(self):
        # Requires PIL package and the "Lenna" image.
        image_path = Path.joinpath(self.examples_path, "lenna.png")
        copyfile(str(image_path), str(Path.joinpath(Path(os.getcwd()), "lenna.png")))

        file_path = Path.joinpath(self.examples_path, "imageData.py")
        runpy.run_path(path_name=str(file_path), run_name="__main__")

        # cleanup
        os.remove("image_example.nix")
        os.remove("lenna.png")

    def test_image_with_metadata(self):
        # Requires PIL package and the "Lenna" image.
        image_path = Path.joinpath(self.examples_path, "lenna.png")
        copyfile(str(image_path), str(Path.joinpath(Path(os.getcwd()), "lenna.png")))

        file_path = Path.joinpath(self.examples_path, "imageWithMetadata.py")
        runpy.run_path(path_name=str(file_path), run_name="__main__")

        # cleanup
        os.remove("image_with_source_example.h5")
        os.remove("image_with_metadata.png")
        os.remove("lenna.png")

    def test_irregularly_sampled_data(self):
        file_path = Path.joinpath(self.examples_path, "irregularlySampledData.py")
        runpy.run_path(path_name=str(file_path), run_name="__main__")
        # cleanup
        os.remove("irregular_data_example.nix")

    def test_lif(self):
        file_path = Path.joinpath(self.examples_path, "lif.py")
        runpy.run_path(path_name=str(file_path), run_name="__main__")

    def test_multiple_points(self):
        file_path = Path.joinpath(self.examples_path, "multiple_points.py")
        runpy.run_path(path_name=str(file_path), run_name="__main__")
        # cleanup
        os.remove("multiple_points.nix")

    def test_multiple_regions(self):
        file_path = Path.joinpath(self.examples_path, "multiple_regions.py")
        runpy.run_path(path_name=str(file_path), run_name="__main__")
        # cleanup
        os.remove("multiple_regions.nix")

    def test_multiple_rois(self):
        # Requires PIL package and the "Lenna" image.
        image_path = Path.joinpath(self.examples_path, "lenna.png")
        copyfile(str(image_path), str(Path.joinpath(Path(os.getcwd()), "lenna.png")))

        file_path = Path.joinpath(self.examples_path, "multipleROIs.py")
        runpy.run_path(path_name=str(file_path), run_name="__main__")

        # cleanup
        os.remove("lenna.png")
        os.remove("multiple_roi.nix")

    def test_range_dimension_link(self):
        file_path = Path.joinpath(self.examples_path, "rangeDimensionLink.py")
        runpy.run_path(path_name=str(file_path), run_name="__main__")
        # cleanup
        os.remove("range_link.nix")

    def test_regularly_sampled_data(self):
        file_path = Path.joinpath(self.examples_path, "regularlySampledData.py")
        runpy.run_path(path_name=str(file_path), run_name="__main__")
        # cleanup
        os.remove("regular_data_example.nix")

    def test_single_roi(self):
        # Requires PIL package and the "Lenna" image.
        image_path = Path.joinpath(self.examples_path, "lenna.png")
        copyfile(str(image_path), str(Path.joinpath(Path(os.getcwd()), "lenna.png")))

        file_path = Path.joinpath(self.examples_path, "singleROI.py")
        runpy.run_path(path_name=str(file_path), run_name="__main__")

        # cleanup
        os.remove("lenna.png")
        os.remove("single_roi.nix")

    def test_sources(self):
        file_path = Path.joinpath(self.examples_path, "sources.py")
        runpy.run_path(path_name=str(file_path), run_name="__main__")
        # cleanup
        os.remove("sources.nix")

    def test_spike_features(self):
        # Requires scipy package and "lif.py"
        lif_path = Path.joinpath(self.examples_path, "lif.py")
        spec = getmod.spec_from_file_location("lif", str(lif_path))
        spec.loader.load_module("lif")

        file_path = Path.joinpath(self.examples_path, "spikeFeatures.py")
        runpy.run_path(path_name=str(file_path), run_name="__main__")

        # cleanup
        os.remove("spike_features.h5")

    def test_spike_tagging(self):
        # Requires "lif.py"
        lif_path = Path.joinpath(self.examples_path, "lif.py")
        spec = getmod.spec_from_file_location("lif", str(lif_path))
        spec.loader.load_module("lif")

        file_path = Path.joinpath(self.examples_path, "spikeTagging.py")
        runpy.run_path(path_name=str(file_path), run_name="__main__")

        # cleanup
        os.remove("spike_tagging.nix")

    def test_tabular_data(self):
        file_path = Path.joinpath(self.examples_path, "tabulardata.py")
        runpy.run_path(path_name=str(file_path), run_name="__main__")
        # cleanup
        os.remove("dataframe.nix")

    def test_tagged_feature(self):
        # Requires scipy package and "lif.py"
        lif_path = Path.joinpath(self.examples_path, "lif.py")
        spec = getmod.spec_from_file_location("lif", str(lif_path))
        spec.loader.load_module("lif")

        file_path = Path.joinpath(self.examples_path, "taggedFeature.py")
        runpy.run_path(path_name=str(file_path), run_name="__main__")

        # cleanup
        os.remove("spike_features.nix")

    def test_tagging_example(self):
        # Requires scipy package
        file_path = Path.joinpath(self.examples_path, "tagging_example.py")
        runpy.run_path(path_name=str(file_path), run_name="__main__")

        # cleanup
        os.remove("tagging1.nix")

    def test_tagging_nd(self):
        # not testing any nix feature
        # file_path = Path.joinpath(self.examples_path, "tagging_nd.py")
        # runpy.run_path(path_name=str(file_path), run_name="__main__")
        pass

    def test_untagged_feature(self):
        # Requires scipy package and "lif.py"
        lif_path = Path.joinpath(self.examples_path, "lif.py")
        spec = getmod.spec_from_file_location("lif", str(lif_path))
        spec.loader.load_module("lif")

        file_path = Path.joinpath(self.examples_path, "untaggedFeature.py")
        runpy.run_path(path_name=str(file_path), run_name="__main__")

        # cleanup
        os.remove("untagged_feature.h5")
