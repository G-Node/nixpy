#include "testutil.hpp"
#include <nix.hpp>

int main(int argc, char* argv[]) {
    if (argc != 2) {
        std::cerr << "Please specify a nix file (and nothing else)" << std::endl;
        return 1;
    }
    std::string fname = argv[1];
    nix::File nf = nix::File::open(fname, nix::FileMode::ReadOnly);

    int idx = 0, errcount = 0, df_no = 7;
    std::string expname, exptp;
    std::vector<nix::Variant> idx_col(4), com_col(4);
    const auto &block = nf.getBlock("test_block");
    for (const auto &df : block.dataFrames()) {
        expname = "df_" + nix::util::numToStr(idx);
        errcount += compare(true, block.hasDataFrame(expname));
        if (idx == 4){
            errcount += compare(6, static_cast<int>(df.columns().size()));
            }
        else if (idx == 5) {
        errcount += compare(5, static_cast<int>(df.rows()));
        }
        else{
            errcount += compare(5, static_cast<int>(df.columns().size()));
            errcount += compare(4, static_cast<int>(df.rows()));
            }

        exptp = "df type " + nix::util::numToStr(idx++);
        errcount += compare(expname, df.name());
        errcount += compare(exptp, df.type());
    }
    return errcount;
}
