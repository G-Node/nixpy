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
    for (const auto &group : block.groups()) {
        expname = "group_" + nix::util::numToStr(idx);
        expdef = "group definition " + nix::util::numToStr(10 * idx++);
        errcount += compare(expname, group.name());
        errcount += compare("grouptype", group.type());
        errcount += compare(expdef, group.definition());
    }
    return errcount;
}
