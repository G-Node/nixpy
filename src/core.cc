#include <boost/python.hpp>
#include <boost/optional/optional.hpp>
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
    boost::python::list l = boost::python::list();

    for(auto& item : vec) {
      l.append(item);
    }

    return boost::python::incref(l.ptr());
  }
};

template<typename T>
struct option_transmogrify {
  static PyObject* convert(const boost::optional<T>& opt) {
    if (opt == boost::none) {
      Py_RETURN_NONE;
    }

    return boost::python::incref(boost::python::object(*opt).ptr());
  }

  typedef boost::python::converter::rvalue_from_python_stage1_data py_s1_data;
  typedef boost::python::converter::rvalue_from_python_storage<boost::optional<T>> py_storage;

  static void register_from_python() {
    boost::python::converter::registry::push_back(is_convertible,
                                                  construct,
                                                  boost::python::type_id<boost::optional<T>>());
  }

  static void* is_convertible(PyObject *obj) {
    return (obj == Py_None || PyString_Check(obj)) ? obj : nullptr;
  }

  static void construct(PyObject *obj, py_s1_data *data) {
    using namespace boost::python::converter;

    void *raw = static_cast<void *>(reinterpret_cast<py_storage *>(data)->storage.bytes);
    if (obj == Py_None) {
      new (raw) boost::optional<T>{};
    } else {
      std::string value(PyString_AsString(obj));
      std::cout << value << std::endl;
      new (raw) boost::optional<T>(value);
    }
    data->convertible = raw;
  }
};

static void
nix_data_array_label_setter(nix::DataArray &da, const boost::optional<std::string> &lbl)
{
  if (lbl == boost::none) {
    da.label(boost::none);
  } else {
    da.label(*lbl);
  }
}

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
    .add_property("label", static_cast<boost::optional<std::string>(nix::DataArray::*)() const>(&nix::DataArray::label),
                           nix_data_array_label_setter)
    .def("has_data", &nix::DataArray::hasData)
    ;

  to_python_converter<std::vector<nix::Block>, vector_transmogrify<nix::Block>>();
  to_python_converter<std::vector<nix::DataArray>, vector_transmogrify<nix::DataArray>>();
  to_python_converter<boost::optional<std::string>, option_transmogrify<std::string>>();
  option_transmogrify<std::string>::register_from_python();
}
