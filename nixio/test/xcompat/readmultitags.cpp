#include "testutil.hpp"
#include <nix.hpp>


int main(int argc, char* argv[]) {
    if (argc != 2) {
        std::cerr << "Please specify a nix file (and nothing else)" << std::endl;
        return 1;
    }
    std::string fname = argv[1];
    nix::File nf = nix::File::open(fname, nix::FileMode::ReadOnly);

    int idx = 0, gidx = 0, errcount = 0;
    std::string expname, expdef;
    const auto &block = nf.getBlock("test_block");
    const auto &grp = block.getGroup("test_group");
    for (const auto &mt : block.multiTags()) {
        expname = "mt_" + nix::util::numToStr(idx);
        errcount += compare(expname, mt.name());
        errcount += compare("some multi tag", mt.type());
        //extent and positions
        nix::NDSize extentSize  = {idx*10};
        if (idx == 1) {
            errcount += compare(mt.positions().dataExtent(), extentSize);
        } else if (idx == 5) {
            extentSize = {5,5};
            errcount += compare(mt.positions().dataExtent(), extentSize);
            errcount += compare(mt.extents().dataExtent(), extentSize);
        } else {
            errcount += compare(mt.positions().dataExtent(), extentSize);
            errcount += compare(extentSize, mt.extents().dataExtent());
        }
        //reference and unit
        if (idx ==2){
            errcount += compare(mt.units(), std::vector<std::string>{"ms"});
            errcount += compare(static_cast<int>(mt.references().size()), 1);
            nix::NDSize refSize  = {13};
            const auto &ref = mt.getReference("ref");
            errcount += compare(ref.dataExtent(), refSize);
            const auto &rdim = ref.dimensions()[0].asRangeDimension();
            errcount += compare(*rdim.label(), "A");
            errcount += compare(rdim.ticks(), std::vector<double>{0.1, 0.2, 0.3});
        } else {
            errcount += compare(mt.units(), std::vector<std::string>{"mV", "s", "Hz"});
            errcount += compare(static_cast<int>(mt.references().size()), 0);
        }
        //feature
        if (idx == 3) {
        nix::NDSize feaSize  = {200};
            errcount += compare(mt.hasFeature("feature"), true);
            const auto &fea = mt.getFeature("feature");
            errcount += compare(fea.data().dataExtent(), feaSize);
        } else {
            errcount += compare(mt.hasFeature("feature"), false);
        }
        //group append
        if(idx % 3 == 0) {
            errcount += compare(grp.getMultiTag(gidx++).id(), mt.id());
        }
        expdef = "mt def " + nix::util::numToStr(10 * idx++);
        errcount += compare(expdef, mt.definition());

    }


    return errcount;
}
