import nixio
import numpy as np


def main():
    nixfile = nixio.File.open("sources.nix", mode=nixio.FileMode.Overwrite)
    block = nixfile.create_block("source example block", "session")

    subject = block.create_source('subject A', 'nix.experimental_subject')
    subject.definition = 'The experimental subject used in this experiment'

    brain_region = subject.create_source('hippocampus', 'nix.experimental_subject.subject')

    cell_a = brain_region.create_source('Cell 1', 'nix.experimental_subject.cell')
    cell_b = brain_region.create_source('Cell 2', 'nix.experimental_subject.cell')

    data_from_subject = block.create_data_array("subject data", "nix.sampled.time_series", data=np.random.randn(100))
    data_from_subject.append_sampled_dimension(1, unit="s", label="time")
    data_from_subject.sources.append(subject)

    data_from_cell_a = block.create_data_array("cell a data", "nix.sampled.time_series", data=np.sin(np.arange(0., 10000., 0.001) * 2 * np.pi * 15))
    data_from_cell_a.append_sampled_dimension(0.001, label="time", unit="s")
    data_from_cell_a.sources.append(cell_a)

    data_from_cell_b = block.create_data_array("cell b data", "nix.sampled.time_series", data=np.sin(np.arange(0., 10000., 0.001) * 2 * np.pi * 5))
    data_from_cell_b.append_sampled_dimension(0.001, label="time", unit="s")
    data_from_cell_b.sources.append(cell_b)

    subject_metadata = nixfile.create_section("subject A", "odml.subject")
    subject_metadata["species"] = "Mus musculus"
    subject_metadata["age"] = "p20"
    subject_metadata["weight"] = 32.5
    subject_metadata.props["weight"].unit = "g"
    subject.metadata = subject_metadata

    cell_a_metadata = subject_metadata.create_section("Cell 1", "odml.cell")
    cell_a_metadata["Type"] = "pyramidal"
    cell_a_metadata["BrainSubregion"] = "CA1"
    cell_a_metadata["BaselineRate"] = 15
    cell_a_metadata.props["BaselineRate"].unit = "Hz"
    cell_a_metadata["Layer"] = "4"
    cell_a.metadata = cell_a_metadata

    cell_b_metadata = subject_metadata.create_section("Cell 2", "odml.cell")
    cell_b_metadata["Type"] = "pyramidal"
    cell_b_metadata["BrainSubregion"] = "CA1"
    cell_b_metadata["BaselineRate"] = 5
    cell_b_metadata.props["BaselineRate"].unit = "Hz"
    cell_b_metadata["Layer"] = 5
    cell_b.metadata = cell_b_metadata

    print("block sources:", block.sources)
    print("subject sources:", subject.sources)
    print("brain region sources:", brain_region.sources)

    src = cell_a.find_sources(lambda s: "subject.cell" in s.type)[0]

    print("Source:", src)
    print("Source metadata:")
    src.metadata.pprint()

    print(cell_a.referring_data_arrays)

    nixfile.close()


if __name__ == "__main__":
    main()
