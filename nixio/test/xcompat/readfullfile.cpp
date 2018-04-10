#include "testutil.hpp"
#include <nix.hpp>


int main(int argc, char* argv[]) {
    if (argc != 2) {
        std::cerr << "Please specify a nix file (and nothing else)" << std::endl;
        return 1;
    }
    std::string fname = argv[1];
    nix::File nf = nix::File::open(fname, nix::FileMode::ReadOnly);

    int errcount = 0;
    errcount += testassert(3 == nf.blockCount(), "Block count mismatch");

    // Check first block attrs before descending
    auto block = nf.getBlock(0);
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
        errcount += testassert(2 == block.groupCount(), "Group count mismatch");
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

    errcount += testassert(block.dataArrayCount() == 4, "DataArray count mismatch in first Block");
    errcount += testassert(group.dataArrayCount() == 1, "DataArray count mismatch in first Group");

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
    errcount += testassert(1 == block.tagCount(), "Tag count mismatch");
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
    errcount += compare(nix::NDSize({6}), feature.data().dataExtent());
    std::vector<float_t> featdata(6);
    feature.data().getData(nix::DataType::Float, featdata.data(), {6}, {});
    errcount += compare({0.4, 0.41, 0.49, 0.1, 0.1, 0.1}, featdata);

    // MultiTag
    errcount += testassert(1 == block.multiTagCount(), "MultiTag count mismatch");
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

    errcount += compare(nix::NDSize({1, 3}), posmt.dataExtent());
    std::vector<float_t> posdata(3*1, 1);
    posmt.getData(nix::DataType::Float, posdata.data(), {1, 3}, {});
    errcount += compare({0, 0.1, 10.1}, posdata);
    errcount += testassert(posmt.dataType() == nix::DataType::Double, "Array dataType mismatch");

    errcount += compare(nix::NDSize({1, 3}), extmt.dataExtent());
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
    errcount += testassert(block.dataArrayCount() == 1, "DataArray count mismatch in second Block");
    da = block.getDataArray(0);
    errcount += compare("FA001", da.name());
    errcount += compare("Primary data", da.type());
    errcount += testassert(nix::DataType::Int64 == da.dataType(), "Array DataType mismatch (Block 1; DataArray 0)");

    return errcount;
}
