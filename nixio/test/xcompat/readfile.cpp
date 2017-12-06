#include <nix.hpp>


int main(int argc, char* argv[]) {
    if (argc != 2) {
        std::cerr << "Please specify a nix file" << std::endl;
        return 1;
    }
    std::string fname = argv[1];
    std::cout << "Validating " << fname << std::endl;
    nix::File nf = nix::File::open(fname);
    nix::valid::Result res = nf.validate();
    std::vector<nix::valid::Message> errors = res.getErrors();
    std::vector<nix::valid::Message> warnings = res.getWarnings();

    int nerrors = errors.size();
    int nwarns = warnings.size();

    std::cout << "Validation complete" << std::endl;
    if (nerrors + nwarns > 0) {
        std::cout << "Errors:   " << nerrors << std::endl;
        for (auto err : errors) {
            std::cout << err.msg << std::endl;
        }
        std::cout << "Warnings: " << nwarns <<  std::endl;
        for (auto wrn : warnings) {
            std::cout << wrn.msg << std::endl;
        }
    } else {
        std::cout << fname << " is a valid NIX file." << std::endl;
    }
    return 0;
}
