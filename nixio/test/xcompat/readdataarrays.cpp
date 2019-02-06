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
    for (const auto &da : block.dataArrays()) {
        expname = "data_" + nix::util::numToStr(idx);
        if (idx%2==0){
            errcount += compare(*da.expansionOrigin() , 100.0);
            const auto &group  = block.getGroup("test_group");
            size_t z = idx/2;
            errcount += compare(group.getDataArray(z).name(), da.name());
            errcount += compare(group.getDataArray(z).id(), block.getDataArray(idx).id());
        }
        if (idx%3 == 0){
            std::vector<double> tmpPoly = {0.1, 0.2, 0.3};
            errcount += compare(da.polynomCoefficients(), tmpPoly);
        } else{
            errcount += compare(static_cast<int>(da.polynomCoefficients().size()), 0);
        }
        // dimensions
        if (idx == 5){
            auto rd = da.getDimension(1);
            errcount += compare(rd.dimensionType(), nix::DimensionType::Range);
            nix::RangeDimension rangeDim;
            rangeDim = rd;
            std::string u = "ms";
            errcount += compare(*rangeDim.unit(), u);
            errcount += compare(rangeDim.ticks(), {1.2 ,2.4});
            errcount += compare(*da.unit(), "mV");
        } else if (idx == 6){
            auto setd = da.getDimension(1);
            auto sampled = da.getDimension(2);
            errcount += compare(setd.dimensionType(), nix::DimensionType::Set);
            errcount += compare(sampled.dimensionType(), nix::DimensionType::Sample);
            nix::SetDimension setDim;
            setDim = setd;
            nix::SampledDimension sampledDim;
            sampledDim = sampled;
            errcount += compare(*sampledDim.unit(), "s");
            errcount += compare(*sampledDim.label(), "dim_label");
            errcount += compare(sampledDim.samplingInterval(), 1.0);
            errcount += compare(*sampledDim.offset(), 1.0);
            errcount += compare(setDim.labels(), {"a", "b"});
        }

        expdef = "da definition " + nix::util::numToStr(idx++);
        errcount += compare(expname, da.name());
        errcount += compare(expdef, da.definition());
    }
    return errcount;
}
