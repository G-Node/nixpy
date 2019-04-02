#include "testutil.hpp"
#include <nix.hpp>


int main(int argc, char* argv[]) {
    if (argc != 2) {
        std::cerr << "Please specify a nix file (and nothing else)" << std::endl;
        return 1;
    }
    std::string fname = argv[1];
    nix::File nf = nix::File::open(fname, nix::FileMode::ReadOnly);

    int idx = 0, errcount = 0;
    std::string expname, expdef;
    const auto &block = nf.getBlock("test_block");
    errcount += compare(static_cast<int>(block.tagCount()), 8);
    for (const auto &tag : block.tags()) {
        expname = "tag_" + nix::util::numToStr(idx);
        errcount += compare(tag.type(), "atag");
        errcount += compare(expname, tag.name());
        std::vector<std::string> units;
        if (idx == 0){
            units = {"V", "ms"};
        } else{
           units = {"mV", "s"};
        }
        errcount += compare(tag.units(), units);
        int positionLen = idx*2;
        if (idx == 2) {
            positionLen = 5;
        }
        errcount += compare(positionLen, static_cast<int>(tag.position().size()));
        errcount += compare(positionLen, static_cast<int>(tag.extent().size()));
        if (idx == 5){
            errcount += compare(1, static_cast<int>(tag.featureCount()));
        } else {
            errcount += compare(0, static_cast<int>(tag.featureCount()));
        }
        expdef = "tag def " + nix::util::numToStr(1*idx++);
        errcount += compare(expdef, tag.definition());
    }
    const auto &grp = block.getGroup("test_group");
    nix::ndsize_t bidx = 3, gidx = 1;
    errcount += compare(grp.getTag(gidx).id(), block.getTag(bidx).id());
    return errcount;
}
