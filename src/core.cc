
#include <boost/python.hpp>
#include <nix.hpp>


static nix::File
nix_file_open(std::string path)
{
  return nix::File::open(path);
}

static std::vector<nix::Block>
nix_file_blocks(const nix::File &f)
{
  return f.blocks();
}

static std::vector<nix::DataArray>
nix_block_data_arrays(const nix::Block &b)
{
  return b.dataArrays();
}

template<typename T>
struct vector_transmogrify {
  static PyObject* convert(const std::vector<T>& vec) {
    boost::python::list* l = new boost::python::list();

    for(auto& item : vec) {
      l->append(item);
    }

    return l->ptr();
  }
};


BOOST_PYTHON_MODULE(core)
{
  using namespace boost::python;

  class_<nix::File>("File")
    .add_property("version", &nix::File::version)
    .def("open", nix_file_open)
    .def("blocks", nix_file_blocks)
    .def("create_block", &nix::File::createBlock)
    .def(self == other<nix::File>())
    .staticmethod("open")
    ;

  class_<nix::Block>("Block")
    .def("create_data_array", &nix::Block::createDataArray)
    .def("data_array_count", &nix::Block::dataArrayCount)
    .def("data_arrays", nix_block_data_arrays)
    .def(self == self)
    ;


  class_<nix::DataArray>("DataArray")
    .def("has_data", &nix::DataArray::hasData)
    ;

  to_python_converter<std::vector<nix::Block>, vector_transmogrify<nix::Block>>();
  to_python_converter<std::vector<nix::DataArray>, vector_transmogrify<nix::DataArray>>();
}
