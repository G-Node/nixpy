#include <boost/python.hpp>
#include <boost/optional/optional.hpp>

#include <nix.hpp>
#include "transmorgify.hpp"
#include "accessors.hpp"

#include "PyEntity.hpp"

using namespace boost::python;
using namespace nix;
using namespace base;
using namespace nixpy;




BOOST_PYTHON_MODULE(core)
{
    // set options for doc strings
    // show user defined / show py signatures / don't show cpp signatures
    docstring_options local_docstring_options(true, true, false);

    PyResult::do_export();
    PyFile::do_export();

    PySection::do_export();
    PyProperty::do_export();

    PyBlock::do_export();
    PySource::do_export();
    PyDataSet::do_export();
    PyDataArray::do_export();
    PyDimensions::do_export();
    PyFeature::do_export();
    PyTag::do_export();
    PyMultiTag::do_export();
    PyGroup::do_export();

    PyException::do_export();


    to_python_converter<boost::optional<std::string>, option_transmogrify<std::string>>();
    option_transmogrify<std::string>::register_from_python();

    to_python_converter<std::vector<std::string>, vector_transmogrify<std::string>>();
    vector_transmogrify<std::string>::register_from_python();

    to_python_converter<std::vector<double>, vector_transmogrify<double>>();
    vector_transmogrify<double>::register_from_python();

    to_python_converter<std::vector<int>, vector_transmogrify<int>>();
    vector_transmogrify<int>::register_from_python();

    to_python_converter<boost::optional<double>, option_transmogrify<double>>();
    option_transmogrify<double>::register_from_python();

    to_python_converter<NDSize, ndsize_transmogrify>();
    ndsize_transmogrify::register_from_python();
}
