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

int compare(const std::vector<std::string> &a, const std::vector<std::string> &b) {
    if (a != b) {
        std::cout << "Mismatch in string vectors" << std::endl;
        std::cout << "Expected {";
        for (const auto& i : a) {
            std::cout << i << " ";
        }
        std::cout << "} got {";
        for (const auto& i : b) {
            std::cout << i << " ";

        }
        std::cout << "}" << std::endl;
        return 1;
    }
    return 0;
}

template <typename T>
int compare(const T a, const T b) {
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

template <typename T>
int compare(const std::vector<T> &a, const std::vector<T> &b, std::string name = "") {
    if (a != b) {
        std::cout << "Mismatch in data vectors";
        if (name != "") {
            std::cout << " (name: " << name << ")";
        }
        std::cout << std::endl;
        std::cout << "Expected {";
        for (const auto& i : a) {
            std::cout << i << " ";
        }
        std::cout << "} got {";
        for (const auto& i : b) {
            std::cout << i << " ";

        }
        std::cout << "}" << std::endl;
        return 1;
    }
    return 0;
}

int compare(const nix::NDSize &a, const nix::NDSize &b, std::string name = "") {
    if (a != b) {
        std::cout << "Mismatch in data extents";
        if (name != "") {
            std::cout << " (name: " << name << ")";
        }
        std::cout << std::endl;
        std::cout << "Exp " << a << "Got " << b << std::endl;
        return 1;
    }
    return 0;
}

int istrue(bool cond, std::string message = "") {
    if (!cond && message != "") {
        std::cout << message << std::endl;
    }
    return !cond;
}
