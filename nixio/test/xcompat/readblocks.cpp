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
    for (const auto &block : nf.blocks()) {
        expname = "test_block" + nix::util::numToStr(idx);
        expdef = "definition block " + nix::util::numToStr(idx++);
        errcount += compare(expname, block.name());
        errcount += compare("blocktype", block.type());
        errcount += compare(expdef, block.definition());
    }
    return errcount;
}
