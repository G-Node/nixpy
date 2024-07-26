import sys
import runpy
import pytest
import unittest
import importlib.util
import importlib.machinery
import matplotlib.pyplot as plt

from pathlib import Path
from shutil import copyfile

TEST_IMAGE = "lenna.png"

@pytest.mark.skip(reason="docs tests often leads to errors during ci")
class TestDocumentationExamples(unittest.TestCase):

    examples_path = Path("docs/source/examples")

    def run_script(self, script_name):
        file_path = Path.joinpath(self.examples_path, script_name)
        runpy.run_path(path_name=str(file_path), run_name="__main__")

    def handle_lif(self):
        lif_path = Path.joinpath(self.examples_path, "lif.py")
        spec = importlib.util.spec_from_file_location("lif", lif_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        sys.modules["lif"] = module

    def handle_image(self):
        image_path = Path.joinpath(self.examples_path, TEST_IMAGE)
        copyfile(str(image_path), str(Path.joinpath(Path(Path.cwd()), TEST_IMAGE)))

    def setUp(self):
        curr_path = Path.cwd()
        if curr_path.stem == "nixpy":
            self.examples_path = Path.joinpath(Path(curr_path),
                                               "docs", "source", "examples")
        elif curr_path.stem == "nixio":
            self.examples_path = Path.joinpath(Path(curr_path).parent,
                                               "docs", "source", "examples")
        elif curr_path.stem == "test":
            self.examples_path = Path.joinpath(Path(curr_path).parent.parent,
                                               "docs", "source", "examples")

        util_path = Path.joinpath(self.examples_path, "docutils.py")
        spec = importlib.util.spec_from_file_location("docutils", util_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        sys.modules["docutils"] = module

        # Render matplotlib plots non-blocking
        plt.ion()

    def tearDown(self):
        plt.close("all")
        plt.ioff()
        if Path.exists(Path("TEST_IMAGE")):
            Path.unlink(Path(TEST_IMAGE), True)

    def test_annotations(self):
        self.run_script("annotations.py")
        # cleanup
        Path.unlink(Path("annotations.nix"), True)

    def test_category_data(self):
        self.run_script("categoryData.py")
        # cleanup
        Path.unlink(Path("categoryData.nix"), True)

    def test_continuous_recording(self):
        self.run_script("continuousRecording.py")
        # cleanup
        Path.unlink(Path("continuous_recording.nix"), True)

    def test_file_create(self):
        self.run_script("fileCreate.py")
        # cleanup
        Path.unlink(Path("file_create_example.nix"), True)

    def test_image_data(self):
        # test will open image with an external program; does not work on windows
        if sys.platform == 'linux':
            # Requires PIL package and the "Lenna" image.
            self.handle_image()
            self.run_script("imageData.py")
            # cleanup
            Path.unlink(Path("image_example.nix"), True)

    def test_image_with_metadata(self):
        # Requires PIL package and the "Lenna" image.
        self.handle_image()
        self.run_script("imageWithMetadata.py")
        # cleanup
        Path.unlink(Path("image_with_source_example.h5"), True)
        Path.unlink(Path("image_with_metadata.png"), True)

    def test_irregularly_sampled_data(self):
        self.run_script("irregularlySampledData.py")
        # cleanup
        Path.unlink(Path("irregular_data_example.nix"), True)

    def test_lif(self):
        self.run_script("lif.py")

    def test_multiple_points(self):
        self.run_script("multiple_points.py")
        # cleanup
        Path.unlink(Path("multiple_points.nix"), True)

    def test_multiple_regions(self):
        self.run_script("multiple_regions.py")
        # cleanup
        Path.unlink(Path("multiple_regions.nix"), True)

    def test_multiple_rois(self):
        # Requires PIL package and the "Lenna" image.
        self.handle_image()
        self.run_script("multipleROIs.py")
        # cleanup
        Path.unlink(Path("multiple_roi.nix"), True)

    def test_range_dimension_link(self):
        self.run_script("rangeDimensionLink.py")
        # cleanup
        Path.unlink(Path("range_link.nix"), True)

    def test_regularly_sampled_data(self):
        self.run_script("regularlySampledData.py")
        # cleanup
        Path.unlink(Path("regular_data_example.nix"), True)

    def test_single_roi(self):
        # test will open image with an external program; does not work on windows
        if sys.platform == 'linux':
            # Requires PIL package and the "Lenna" image.
            self.handle_image()
            self.run_script("singleROI.py")
            # cleanup
            Path.unlink(Path("single_roi.nix"), True)

    def test_sources(self):
        self.run_script("sources.py")
        # cleanup
        Path.unlink(Path("sources.nix"), True)

    def test_spike_features(self):
        # Requires scipy package and "lif.py"
        self.handle_lif()
        self.run_script("spikeFeatures.py")
        # cleanup
        Path.unlink(Path("spike_features.h5"), True)

    def test_spike_tagging(self):
        # Requires "lif.py"
        self.handle_lif()
        self.run_script("spikeTagging.py")
        # cleanup
        Path.unlink(Path("spike_tagging.nix"), True)

    def test_tabular_data(self):
        self.run_script("tabulardata.py")
        # cleanup
        Path.unlink(Path("dataframe.nix"), True)

    def test_tagged_feature(self):
        # Requires scipy package and "lif.py"
        self.handle_lif()
        self.run_script("taggedFeature.py")
        # cleanup
        Path.unlink(Path("spike_features.nix"), True)

    def test_tagging_example(self):
        # Requires scipy package
        self.run_script("tagging_example.py")
        # cleanup
        Path.unlink(Path("tagging1.nix"), True)

    def test_tagging_nd(self):
        # not testing any nix feature
        # self.run_script("tagging_nd.py")
        pass

    def test_untagged_feature(self):
        # Requires scipy package and "lif.py"
        self.handle_lif()
        self.run_script("untaggedFeature.py")
        # cleanup
        Path.unlink(Path("untagged_feature.h5"), True)
