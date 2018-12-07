#include "testutil.hpp"
#include <nix.hpp>


std::vector<nix::DataType> dtypes = {
    nix::DataType::UInt8,
    nix::DataType::UInt16,
    nix::DataType::UInt32,
    nix::DataType::UInt64,
    nix::DataType::Int8,
    nix::DataType::Int16,
    nix::DataType::Int32,
    nix::DataType::Int64,
    nix::DataType::Float,
    nix::DataType::Double,
    nix::DataType::String,
    nix::DataType::Bool
};


int main(int argc, char* argv[]) {
    if (argc != 2) {
        std::cerr << "Please specify a nix file (and nothing else)" << std::endl;
        return 1;
    }
    std::string fname = argv[1];
    nix::File nf = nix::File::open(fname, nix::FileMode::Overwrite);

    auto block = nf.createBlock("blockyblock", "ablocktype of thing");
    block.definition("I am a test block");
    block.forceCreatedAt(1500001000);

    block = nf.createBlock("I am another block", "void");
    block.definition("Void block of stuff");
    block.forceCreatedAt(1500002000);

    block = nf.createBlock("Block C", "a block of stuff");
    block.definition("The third block");
    block.forceCreatedAt(1500003000);

    int idx = 0;
    char name [7];
    nix::Group group;
    for (auto bl : nf.blocks()) {
        sprintf(name, "grp%02d0", idx);
        group = bl.createGroup(name, "grp");
        group.definition("group 0");
        group.forceCreatedAt(bl.createdAt());
        sprintf(name, "grp%02d1", idx);
        group = bl.createGroup(name, "grp");
        group.definition("group 1");
        group.forceCreatedAt(bl.createdAt());
        idx++;
    }

    block = nf.getBlock(0);
    std::vector<double> datadbl = {1, 2, 10, 9, 1, 3};
    auto da = block.createDataArray("bunchodata", "recordings", nix::DataType::Double, nix::NDSize{2, 3});
    da.setData(nix::DataType::Double, datadbl.data(), nix::NDSize{2, 3}, nix::NDSize{0, 0});
    da.definition("A silly little data array");
    auto smpldim = da.appendSampledDimension(0.1);
    smpldim.unit("ms");
    smpldim.label("time");
    auto setdim = da.appendSetDimension();
    setdim.labels({"a", "b"});
    group = block.getGroup(0);
    group.addDataArray(da);

    nix::Column name = new nix::Column ();
    auto df = block.creteDataFrame("paneldata", "filing", std::)

    datadbl = {0.4, 0.41, 0.49, 0.1, 0.1, 0.1};
    auto featda = block.createDataArray("feat-da", "tag-feature", nix::DataType::Double, nix::NDSize{6});
    featda.setData(nix::DataType::Double, datadbl.data(), nix::NDSize{6}, nix::NDSize{0});
    auto tag = block.createTag("tagu", "tagging", {1, 0});
    tag.extent({1, 10});
    tag.units({"mV", "s"});
    tag.definition("tags ahoy");
    tag.addReference(da);
    group.addTag(tag);
    tag.createFeature(featda, nix::LinkType::Untagged);

    auto mtag = block.createMultiTag("mtagu", "multi tagging", block.createDataArray("tag-data", "multi-tagger", nix::DataType::Double, nix::NDSize{1, 3}));
    datadbl = {0, 0.1, 10.1};
    // MultiTag positions array
    da = block.getDataArray("tag-data");
    da.setData(nix::DataType::Double, datadbl.data(), nix::NDSize{1, 3}, nix::NDSize{0, 0});

    smpldim = da.appendSampledDimension(0.01);
    smpldim.unit("s");
    da.appendSetDimension();

    // MultiTag extents array
    datadbl = {0.5, 0.5, 0.5};
    da = block.createDataArray("tag-extents", "multi-tagger", nix::DataType::Double, nix::NDSize{1, 3});
    da.setData(nix::DataType::Double, datadbl.data(), nix::NDSize{1, 3}, nix::NDSize{0, 0});
    mtag.extents(da);
    smpldim = da.appendSampledDimension(0.01);
    smpldim.unit("s");
    da.appendSetDimension();

    std::vector<int64_t> datai64 = {100, 200, 210, 3};
    da = nf.getBlock(1).createDataArray("FA001", "Primary data", nix::DataType::Int64, nix::NDSize{4});
    da.setData(nix::DataType::Int64, datai64.data(), nix::NDSize{4}, nix::NDSize{0});
    da.definition("Some random integers");

    // Source tree
    block = nf.getBlock(0);
    auto src = block.createSource("root-source", "top-level-source");

    // Point all (block's) data arrays to root-source
    for (auto da : block.dataArrays())
        da.addSource(src);

    auto srcd1 = src.createSource("d1-source", "second-level-source");
    src.createSource("d1-source-2", "second-level-source");
    // point first da to d1-source
    block.getDataArray(0).addSource(srcd1);

    // Metadata
    // 3 root sections
    for (auto name : {"mda", "mdb", "mdc"})
        nf.createSection(name, "root-section");

    auto sec = nf.getSection("mdc");

    // 6 sections under third root section
    for (idx = 0; idx < 6; idx++) {
        sprintf(name, "%03d-md", idx);
        sec.createSection(name, "d1-section");
    }

    // Point existing objects to metadata sections
    nf.getBlock(0).metadata(nf.getSection("mdb"));
    nf.getBlock(2).metadata(nf.getSection("mdb"));

    nf.getBlock(1).getDataArray(0).metadata(nf.getSection("mda"));
    nf.getBlock(0).getTag(0).metadata(nf.getSection("mdc").getSection(3));

    // Add Tag and MultiTag to Block 2, Group 0
    block = nf.getBlock(2);
    group = block.getGroup(0);
    tag = block.createTag("POI", "TAG", {0, 0});
    tag.extent({1920, 1080});
    tag.units({"mm", "mm"});

    auto png = block.createDataArray("some-sort-of-image?", "png", nix::DataType::Double, nix::NDSize{3840, 2160});
    tag.createFeature(png, nix::LinkType::Indexed);

    auto newmtpositions = block.createDataArray("nu-pos", "multi-tag-positions", nix::DataType::Double, nix::NDSize{10, 3});
    auto newmtag = block.createMultiTag("nu-mt", "multi-tag (new)", newmtpositions);
    group.addTag(tag);
    group.addMultiTag(newmtag);

    // Data with RangeDimension
    std::vector<int32_t> datai32 = {0, 1, 23};
    block = nf.getBlock(2);
    da = block.createDataArray("the ticker", "range-dim-array", nix::DataType::Int32, nix::NDSize{3});
    da.setData(nix::DataType::Int32, datai32.data(), nix::NDSize{3}, nix::NDSize{0});
    da.unit("uA");
    datadbl.clear();
    for (idx = 0; idx < 50; idx++)
        datadbl.push_back(10+(idx*0.1));
    auto rdim = da.appendRangeDimension(datadbl);
    rdim.label("a range dimension");
    rdim.unit("s");

    // Alias RangeDimension
    block = nf.getBlock(1);
    da = block.createDataArray("alias da", "dimticks", nix::DataType::Int32, nix::NDSize{24});
    datadbl.clear();
    for (idx = 0; idx < 24; idx++)
        datadbl.push_back(3+(idx*0.5));
    da.label("alias dimension label");
    da.unit("F");
    da.appendAliasRangeDimension();

    // All types of metadata
    std::vector<nix::Variant> values;
    sec = nf.getSection("mdb");
    auto proptypesmd = sec.createSection("prop-test-parent", "test metadata section");
    auto numbermd = proptypesmd.createSection("numerical metadata", "test metadata section");
    numbermd.createProperty("integer", nix::Variant(int32_t(42)));
    numbermd.createProperty("float", nix::Variant(float(4.2)));
    for (int32_t v : {40, 41, 42, 43, 44, 45})
        values.push_back(nix::Variant(v));
    numbermd.createProperty("integers", values);
    values = {nix::Variant(float(1.1)), nix::Variant(float(10.10))};
    numbermd.createProperty("floats", values);

    auto othermd = proptypesmd.createSection("other metadata", "test metadata section");
    othermd.createProperty("bool", nix::Variant(true));
    othermd.createProperty("false bool", nix::Variant(false));
    othermd.createProperty("bools", {nix::Variant(true), nix::Variant(false), nix::Variant(true)});
    othermd.createProperty("string", nix::Variant("I am a string. Rawr."));
    othermd.createProperty("strings", {nix::Variant("one"), nix::Variant("two"), nix::Variant("twenty")});

    // All types of data
    block = nf.createBlock("datablock", "block of data");

    for (auto dt : dtypes) {
        block.createDataArray(nix::data_type_to_string(dt), "dtype-test-array", dt, nix::NDSize{0});
    }

    return 0;
}
