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

    if (nf.blockCount() != 3) {
        std::cout << "Expected 2 blocks, got " << nf.blockCount() << std::endl;
        errcount++;
    }

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
        if (block.groupCount() != 2) {
            std::cout << "Expected 2 groups, got " << block.groupCount() << std::endl;
            errcount++;
        }
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

    if (block.dataArrayCount() != 4) {
        std::cout << "Expected 2 DataArrays, got " << block.dataArrayCount() << std::endl;
        errcount++;
    }

    if (group.dataArrayCount() != 1) {
        std::cout << "Expected 1 DataArray, got " << group.dataArrayCount() << std::endl;
        errcount++;
    }

    nix::DataArray da = block.getDataArray(0);
    errcount += compare(da.id(), group.getDataArray(0).id());
    errcount += compare("bunchodata", da.name());
    errcount += compare("recordings", da.type());
    errcount += compare("A silly little data array", da.definition());

    // Data
    std::vector<float_t> dadata(2*3, 1);
    da.getData(nix::DataType::Float, dadata.data(), {2, 3}, {});
    errcount += compare(dadata, {1, 2, 10, 9, 1, 3});
    errcount += compare(da.dataExtent(), nix::NDSize({2, 3}));
    errcount += istrue(da.dataType() == nix::DataType::Double, "Array dataType mismatch");

    // DataArray dimensions
    auto dim = da.getDimension(1);
    errcount += istrue(dim.dimensionType() ==  nix::DimensionType::Sample, "Dimension 1 should be Sample type");
    nix::SampledDimension smpldim;
    smpldim = dim;
    errcount += compare(0.1, smpldim.samplingInterval());
    errcount += compare("ms", smpldim.unit());
    errcount += compare("time", smpldim.label());

    dim = da.getDimension(2);
    errcount += istrue(dim.dimensionType() ==  nix::DimensionType::Set, "Dimension 2 should be Set type");
    nix::SetDimension setdim;
    setdim = dim;
    errcount += compare({"a", "b"}, setdim.labels());

    // Tag and MultiTag

    return errcount;
}
