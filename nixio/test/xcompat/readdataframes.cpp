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
    std::vector<nix::DataFrame> df_vector(df_no);
    std::vector<nix::Variant> idx_col(4), com_col(4);
    const auto &block = nf.getBlock("test_block");
    for (int i=0; i<(df_no); i++){
            df_vector[i] =  block.getDataFrame(i);
    }
    for (const auto &df : df_vector) {
        expname = "df_" + nix::util::numToStr(idx);
        errcount += compare(true, block.hasDataFrame(expname));
        if (idx == 4){
            errcount += compare(6, static_cast<int>(df.columns().size()));
//            errcount += compare();
            }
        else if (idx == 5) {
        errcount += compare(5, static_cast<int>(df.rows()));
        }
        else{
            errcount += compare(5, static_cast<int>(df.columns().size()));
            errcount += compare(4, static_cast<int>(df.rows()));
            for (int i=0; i<(5) ;i++){
                df.readColumn(i, idx_col, 4, false);
                df_vector[0].readColumn(i, com_col, 4, false);
                errcount += compare( idx_col, com_col);
                                      }
            }
        exptp = "df type " + nix::util::numToStr(idx++);
        errcount += compare(expname, df.name());
        errcount += compare(exptp, df.type());
    }
    return errcount;
}
