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
    // NOTE: NIXPy doesn't do 'Float' (32)
    // It will probably be easier to add when the bindings are removed
    nix::DataType::Double,
    nix::DataType::Double,
    nix::DataType::String,
    nix::DataType::Bool
};


int checkChildrenCounts(const nix::Block &bl, size_t ngrp, size_t nda, size_t nt, size_t nmt) {
    int errcount = 0;
    errcount += testassert(ngrp == bl.groupCount(), "Group count mismatch in Block " + bl.name());
    errcount += testassert(nda  == bl.dataArrayCount(), "DataArray count mismatch in Block " + bl.name());
    errcount += testassert(nt   == bl.tagCount(), "Tag count mismatch in Block " + bl.name());
    errcount += testassert(nmt  == bl.multiTagCount(), "MultiTag count mismatch in Block " + bl.name());

    return errcount;
}

int checkChildrenCounts(const nix::Group &grp, size_t nda, size_t nt, size_t nmt) {
    int errcount = 0;
    errcount += testassert(nda  == grp.dataArrayCount(), "DataArray count mismatch in Group " + grp.name());
    errcount += testassert(nt   == grp.tagCount(), "Tag count mismatch in Group " + grp.name());
    errcount += testassert(nmt  == grp.multiTagCount(), "MultiTag count mismatch in Group " + grp.name());

    return errcount;
}

int checkObjectCounts(const nix::File &nf) {
    int errcount = 0;
    // Check object counts (Group, DataArray, Tag, MultiTag)
    errcount += testassert(4 == nf.blockCount(), "Block count mismatch");

    errcount += checkChildrenCounts(nf.getBlock(0), 2, 4, 1, 1);
    errcount += checkChildrenCounts(nf.getBlock(1), 2, 2, 0, 0);
    errcount += checkChildrenCounts(nf.getBlock(2), 2, 3, 1, 1);
    errcount += checkChildrenCounts(nf.getBlock(3), 0, 12, 0, 0);

    errcount += checkChildrenCounts(nf.getBlock(0).getGroup(0), 1, 1, 0);
    errcount += checkChildrenCounts(nf.getBlock(0).getGroup(1), 0, 0, 0);

    errcount += checkChildrenCounts(nf.getBlock(1).getGroup(0), 0, 0, 0);
    errcount += checkChildrenCounts(nf.getBlock(1).getGroup(1), 0, 0, 0);

    errcount += checkChildrenCounts(nf.getBlock(2).getGroup(0), 0, 1, 1);
    errcount += checkChildrenCounts(nf.getBlock(2).getGroup(1), 0, 0, 0);

    return errcount;
}

int main(int argc, char* argv[]) {
    if (argc != 2) {
        std::cerr << "Please specify a nix file (and nothing else)" << std::endl;
        return 1;
    }
    std::string fname = argv[1];
    nix::File nf = nix::File::open(fname, nix::FileMode::ReadOnly);

    int errcount = 0;
    errcount += checkObjectCounts(nf);

    auto block = nf.getBlock(0);
    // Check first block attrs before descending
    errcount += compare("blockyblock", block.name());
    errcount += compare("ablocktype of thing", block.type());
    errcount += compare("I am a test block", block.definition());

    block = nf.getBlock(1);
    // Check second block attrs (no children)
    errcount += compare("I am another block", block.name());
    errcount += compare("void", block.type());
    errcount += compare("Void block of stuff", block.definition());

    std::string expname, expdef;
    size_t bidx = 0, gidx = 0;
    for (auto block : nf.blocks()) {
        for (const auto &group : block.groups()) {
            expname = "grp0" + nix::util::numToStr(bidx) + nix::util::numToStr(gidx);
            expdef = expname + "-grp";
            errcount += compare(expname, group.name());
            errcount += compare("grp", group.type());
            errcount += compare(expdef, group.definition());
            errcount += compare(block.createdAt(), group.createdAt());
            gidx++;
        }
        bidx++;
        gidx = 0;
    }

    // DataArray
    block = nf.getBlock(0);
    auto group = block.getGroup(0);

    auto da = block.getDataArray(0);
    errcount += compare(da.id(), group.getDataArray(0).id());
    errcount += compare("bunchodata", da.name());
    errcount += compare("recordings", da.type());
    errcount += compare("A silly little data array", da.definition());

    // Data
    std::vector<float_t> dadata(2*3, 1);
    da.getData(nix::DataType::Float, dadata.data(), {2, 3}, {});
    errcount += compare({1, 2, 10, 9, 1, 3}, dadata);
    errcount += compare({2, 3}, da.dataExtent());
    errcount += testassert(da.dataType() == nix::DataType::Double, "Array dataType mismatch");

    // DataArray dimensions
    auto dim = da.getDimension(1);
    errcount += testassert(dim.dimensionType() ==  nix::DimensionType::Sample, "Dimension 1 should be Sample type");
    nix::SampledDimension smpldim;
    smpldim = dim;
    errcount += compare(0.1, smpldim.samplingInterval());
    errcount += compare("ms", smpldim.unit());
    errcount += compare("time", smpldim.label());

    dim = da.getDimension(2);
    errcount += testassert(dim.dimensionType() ==  nix::DimensionType::Set, "Dimension 2 should be Set type");
    nix::SetDimension setdim;
    setdim = dim;
    errcount += compare({"a", "b"}, setdim.labels());

    // Tag
    auto tag = block.getTag(0);
    errcount += compare("tagu", tag.name());
    errcount += compare("tagging", tag.type());
    errcount += compare("tags ahoy", tag.definition());
    errcount += compare({1, 0}, tag.position());
    errcount += compare({1, 10}, tag.extent());
    errcount += compare({"mV", "s"}, tag.units());
    errcount += compare(da.id(), tag.getReference(0).id());
    errcount += compare(group.getTag(0).id(), tag.id());
    auto feature = tag.getFeature("feat-da");
    errcount += compare(feature.linkType(), nix::LinkType::Untagged);
    errcount += compare(feature.data().id(), block.getDataArray(1).id());
    errcount += compare("feat-da", feature.data().name());
    errcount += compare(nix::NDSize{6}, feature.data().dataExtent());
    std::vector<float_t> featdata(6);
    feature.data().getData(nix::DataType::Float, featdata.data(), {6}, {});
    errcount += compare({0.4, 0.41, 0.49, 0.1, 0.1, 0.1}, featdata);

    // MultiTag
    auto mtag = block.getMultiTag(0);
    errcount += compare("mtagu", mtag.name());
    errcount += compare("multi tagging", mtag.type());
    errcount += compare("", mtag.definition());
    auto posmt = mtag.positions();
    auto extmt = mtag.extents();
    errcount += compare(block.getDataArray(posmt.name()).id(), posmt.id());
    errcount += compare(block.getDataArray(extmt.name()).id(), extmt.id());

    // MultiTag data
    errcount += compare("tag-data", posmt.name());
    errcount += compare("multi-tagger", posmt.type());
    errcount += compare("tag-extents", extmt.name());
    errcount += compare("multi-tagger", extmt.type());

    errcount += compare(nix::NDSize{1, 3}, posmt.dataExtent());
    std::vector<float_t> posdata(3*1, 1);
    posmt.getData(nix::DataType::Float, posdata.data(), {1, 3}, {});
    errcount += compare({0, 0.1, 10.1}, posdata);
    errcount += testassert(posmt.dataType() == nix::DataType::Double, "Array dataType mismatch");

    errcount += compare(nix::NDSize{1, 3}, extmt.dataExtent());
    std::vector<float_t> extdata(3*1, 1);
    extmt.getData(nix::DataType::Float, extdata.data(), {1, 3}, {});
    errcount += compare({0.5, 0.5, 0.5}, extdata);
    errcount += testassert(extmt.dataType() == nix::DataType::Double, "Array dataType mismatch");

    // MultiTag Position and Extent dimensions
    errcount += testassert(2 == posmt.dimensionCount(), "Dimension count mismatch in posmt");
    dim = posmt.getDimension(2);
    errcount += testassert(dim.dimensionType() == nix::DimensionType::Set, "Dimension 2 should be Set type");

    dim = posmt.getDimension(1);
    errcount += testassert(dim.dimensionType() == nix::DimensionType::Sample, "Dimension 1 should be Sample type");
    smpldim = dim;
    errcount += compare(0.01, smpldim.samplingInterval());
    errcount += compare("s", smpldim.unit());

    errcount += testassert(2 == extmt.dimensionCount(), "Dimension count mismatch in extmt");
    dim = extmt.getDimension(2);
    errcount += testassert(dim.dimensionType() == nix::DimensionType::Set, "Dimension 2 should be Set type");

    dim = extmt.getDimension(1);
    errcount += testassert(dim.dimensionType() == nix::DimensionType::Sample, "Dimension 1 should be Sample type");
    smpldim = dim;
    errcount += compare(0.01, smpldim.samplingInterval());
    errcount += compare("s", smpldim.unit());

    // Tag and MultiTag Block and Group membership
    for (size_t idx = 1; idx < nf.blockCount(); idx++) {
        errcount += testassert(!nf.getBlock(idx).hasTag(tag.id()), "Tag found in incorrect Block");
        errcount += testassert(!nf.getBlock(idx).hasMultiTag(mtag.id()), "MultiTag found in incorrect Block");
    }

    errcount += testassert(!group.hasMultiTag(mtag.id()), "MultiTag found in incorrect Group");
    for (size_t idx = 1; idx < block.groupCount(); idx++) {
        errcount += testassert(!block.getGroup(idx).hasTag(tag.id()), "Tag found in incorrect Group");
        errcount += testassert(!block.getGroup(idx).hasMultiTag(mtag.id()), "MultiTag found in incorrect Group");
    }

    // Second Block DataArray
    block = nf.getBlock(1);
    da = block.getDataArray(0);
    errcount += compare("FA001", da.name());
    errcount += compare("Primary data", da.type());
    errcount += testassert(nix::DataType::Int64 == da.dataType(), "Array DataType mismatch (Block 1; DataArray 0)");

    // Sources
    block = nf.getBlock(0);
    errcount += testassert(1 == block.sourceCount(), "Source count mismatch (Block 0)");
    auto src = block.getSource("root-source");
    errcount += compare("top-level-source", src.type());
    for (auto da : block.dataArrays()) {
        errcount += compare(da.getSource(0).id(), src.id());
    }

    errcount += testassert(2 == src.sourceCount(), "Source count mismatch (Block 0; Source 0)");
    errcount += compare("d1-source", src.getSource(0).name());
    errcount += compare("d1-source-2", src.getSource(1).name());
    errcount += compare("second-level-source", src.getSource(0).type());
    errcount += compare("second-level-source", src.getSource(1).type());

    for (auto s : src.sources()) {
        errcount += testassert(0 == s.sourceCount());
    }

    da = block.getDataArray(0);
    errcount += testassert(2 == da.sourceCount(), "Source count mismatch (Block 0; DataArray 0)");
    errcount += compare(da.getSource(1).id(), block.getSource(0).getSource(0).id());

    // Metadata
    // 3 root sections
    errcount += testassert(3 == nf.sectionCount(), "Section count mismatch (root)");
    errcount += compare(nf.getSection(0).name(), "mda");
    errcount += compare(nf.getSection(1).name(), "mdb");
    errcount += compare(nf.getSection(2).name(), "mdc");
    for (auto s : nf.sections()) {
        errcount += compare("root-section", s.type());
    }

    auto mdc = nf.getSection(2);
    errcount += testassert(6 == mdc.sectionCount(), "Section count mismatch (mdc)");
    char name [6];
    for (int idx = 0; idx < 6; idx++) {
        sprintf(name, "%03d-md", idx);
        errcount += compare("d1-section", mdc.getSection(name).type());
    }

    auto mdb = nf.getSection(1);
    errcount += compare(nf.getBlock(0).metadata().id(), mdb.id());
    errcount += compare(nf.getBlock(2).metadata().id(), mdb.id());

    errcount += compare(nf.getBlock(1).getDataArray(0).metadata().id(), nf.getSection("mda").id());
    errcount += compare(nf.getBlock(0).getTag(0).metadata().id(), nf.getSection("mdc").getSection(3).id());

    block = nf.getBlock(2);
    tag = block.getTag(0);
    errcount += compare("POI", tag.name());
    errcount += compare("TAG", tag.type());
    errcount += compare({0, 0}, tag.position());
    errcount += compare({1920, 1080}, tag.extent());
    errcount += compare({"mm", "mm"}, tag.units());
    errcount += compare(tag.id(), block.getGroup(0).getTag(0).id());

    feature = tag.getFeature("some-sort-of-image?");
    errcount += compare(feature.linkType(), nix::LinkType::Indexed);
    errcount += compare(feature.data().id(), block.getDataArray(0).id());
    errcount += compare("some-sort-of-image?", feature.data().name());
    errcount += compare(nix::NDSize{3840, 2160}, feature.data().dataExtent());

    mtag = block.getMultiTag(0);
    errcount += compare("nu-mt", mtag.name());
    errcount += compare("multi-tag (new)", mtag.type());
    posmt = mtag.positions();
    errcount += compare("nu-pos", posmt.name());
    errcount += compare("multi-tag-positions", posmt.type());
    errcount += compare({10, 3}, posmt.dataExtent());
    errcount += testassert(nix::DataType::Double == posmt.dataType(), "DataType mismatch in nu-pos DataArray");
    errcount += compare(posmt.id(), block.getDataArray(1).id());
    errcount += compare(mtag.id(), block.getGroup(0).getMultiTag(0).id());

    // Data with range dimension
    block = nf.getBlock(2);
    da = block.getDataArray("the ticker");
    std::vector<int32_t> tickerdata(3);
    da.getData(nix::DataType::Int32, tickerdata.data(), nix::NDSize{3}, nix::NDSize{0});
    errcount += compare({0, 1, 23}, tickerdata);
    errcount += compare({3}, da.dataExtent());
    errcount += compare("range-dim-array", da.type());
    errcount += compare("uA", da.unit());
    errcount += testassert(da.dataType() == nix::DataType::Int32, "Array DataType mismatch");
    dim = da.getDimension(1);
    nix::RangeDimension rdim;
    rdim = dim;
    errcount += testassert(rdim.dimensionType() ==  nix::DimensionType::Range, "Dimension 1 should be Range type");

    auto tickdata = rdim.ticks();
    errcount += compare(size_t{50}, tickdata.size());
    errcount += compare("a range dimension", rdim.label());
    errcount += compare("s", rdim.unit());

    // Alias range dimension
    block = nf.getBlock(1);
    da = block.getDataArray("alias da");
    errcount += compare("dimticks", da.type());
    errcount += compare("F", da.unit());
    errcount += compare("alias dimension label", da.label());
    errcount += compare({24}, da.dataExtent());
    std::vector<double> aliasdata(24);
    da.getData(nix::DataType::Double, aliasdata.data(), nix::NDSize{24}, nix::NDSize{0});
    dim = da.getDimension(1);
    rdim = dim;
    errcount += testassert(rdim.dimensionType() ==  nix::DimensionType::Range, "Dimension 1 should be Range type");
    errcount += testassert(rdim.alias(), "Dimension 1 should be alias Range dimension");

    errcount += compare(aliasdata, rdim.ticks());

    // Metadata types
    mdb = nf.getSection("mdb");
    errcount += testassert(1 == mdb.sectionCount(), "mdb child section count mismatch");
    auto proptypesmd = mdb.getSection("prop-test-parent");
    errcount += compare("test metadata section", proptypesmd.type());
    errcount += testassert(2 == proptypesmd.sectionCount(), "prop-test-parent child section count mismatch");

    auto numbermd = proptypesmd.getSection(0);
    errcount += compare("numerical metadata", numbermd.name());
    errcount += compare("test metadata section", numbermd.type());
    errcount += compare(nix::ndsize_t{4}, numbermd.propertyCount());

    auto prop = numbermd.getProperty("integer");
    errcount += compare(nix::ndsize_t{1}, prop.valueCount());
    errcount += compare({nix::Value{int64_t(42)}}, prop.values());

    prop = numbermd.getProperty("float");
    errcount += compare(nix::ndsize_t{1}, prop.valueCount());
    errcount += compare({nix::Value{double(4.2)}}, prop.values());

    prop = numbermd.getProperty("integers");
    errcount += compare(nix::ndsize_t{6}, prop.valueCount());
    std::vector<nix::Value> values(6);
    for (auto idx = 0; idx < 6; idx++)
        values[idx] = nix::Value{int64_t(40 + idx)};
    errcount += compare(values, prop.values());

    prop = numbermd.getProperty("floats");
    errcount += compare(nix::ndsize_t{2}, prop.valueCount());
    errcount += compare({nix::Value{double(1.1)}, nix::Value{double(10.10)}}, prop.values());

    auto othermd = proptypesmd.getSection(1);
    errcount += compare("other metadata", othermd.name());
    errcount += compare("test metadata section", othermd.type());
    errcount += compare(nix::ndsize_t{5}, othermd.propertyCount());

    prop = othermd.getProperty("bool");
    errcount += compare(nix::ndsize_t{1}, prop.valueCount());
    errcount += compare({nix::Value{true}}, prop.values());

    prop = othermd.getProperty("false bool");
    errcount += compare(nix::ndsize_t{1}, prop.valueCount());
    errcount += compare({nix::Value{false}}, prop.values());

    prop = othermd.getProperty("bools");
    errcount += compare(nix::ndsize_t{3}, prop.valueCount());
    errcount += compare({nix::Value{true}, nix::Value{false}, nix::Value{true}}, prop.values());

    prop = othermd.getProperty("string");
    errcount += compare(nix::ndsize_t{1}, prop.valueCount());
    errcount += compare({nix::Value{"I am a string. Rawr."}}, prop.values());

    prop = othermd.getProperty("strings");
    errcount += compare(nix::ndsize_t{3}, prop.valueCount());
    errcount += compare({nix::Value{"one"}, nix::Value{"two"}, nix::Value{"twenty"}}, prop.values());

    block = nf.getBlock("datablock");
    errcount += compare("block of data", block.type());

    for (size_t idx = 0; idx < dtypes.size(); idx++) {
        da = block.getDataArray(idx);
        auto dt = dtypes[idx];
        errcount += compare(dt, da.dataType());
        errcount += compare({1}, da.dataExtent());
    }

    return errcount;
}
