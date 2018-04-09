#include <iostream>
#include <string>
#include <boost/optional.hpp>
#include <nix.hpp>


int compare(const std::string &a, const std::string &b) {
    if (a != b) {
        std::cout << "Expected '" << a << "' got '" << b << "'" << std::endl;
        return 1;
    }
    return 0;
}

template <typename T>
int compare(const std::string &a, boost::optional<T> b) {
    return compare(a, nix::util::deRef(b));
}
