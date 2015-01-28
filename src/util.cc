#include <boost/python.hpp>
#include <boost/optional/optional.hpp>

#include <nix.hpp>
#include <transmorgify.hpp>
#include <accessors.hpp>

#include <PyUtil.hpp>

using namespace boost::python;
using namespace nix;
using namespace base;
using namespace nixpy;


BOOST_PYTHON_MODULE(xtra)
{
    PyUtil::do_export();
}
