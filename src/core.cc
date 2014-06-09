#include <boost/python.hpp>
#include <boost/optional/optional.hpp>

#include <nix.hpp>
#include <transmorgify.hpp>
#include <accessors.hpp>
#include <PyEntity.hpp>

using namespace boost::python;
using namespace nix;
using namespace base;
using namespace nixpy;

static File
nix_file_open ( std::string path ) {
    return File::open ( path );
}

static std::vector<Block>
nix_file_blocks ( const File &f ) {
    return f.blocks();
}

static std::vector<DataArray>
nix_block_data_arrays ( const Block &b ) {
    return b.dataArrays();
}

static void
nix_data_array_label_setter ( DataArray &da, const boost::optional<std::string> &lbl ) {
    if ( lbl == boost::none ) {
        da.label ( boost::none );
    } else {
        da.label ( *lbl );
    }
}


BOOST_PYTHON_MODULE(core)
{

    class_<File>("File")
        .add_property("version", &File::version)
        .def("open", nix_file_open)
        .def("blocks", nix_file_blocks)
        .def("create_block", &File::createBlock)
        .def(self == other<File>())
        .staticmethod("open")
        ;

    // TODO enum classes for Implementation and FileMode

    class_<Value>("Value");

    class_<Property>("Property");

    class_<Section>("Section");

    PyEntityWithMetadata<IBlock>::do_export("IBlock");
    class_<Block, bases<EntityWithMetadata<IBlock>>>("Block")
        .def("create_data_array", &Block::createDataArray)
        .def("data_array_count", &Block::dataArrayCount)
        .def("data_arrays", nix_block_data_arrays)
        .def(self == self)
        ;

    class_<Source>("Source");

    PyEntityWithSources<IDataArray>::do_export("IDataArray");
    class_<DataArray, bases<EntityWithSources<IDataArray>>>("DataArray")
        .add_property("label",
                      OPT_GETTER(std::string, DataArray, label),
                      &nix_data_array_label_setter)
        .def("has_data", &DataArray::hasData)
        ;

    // TODO enum class DataType

    class_<Dimension>("Dimension");

    class_<SampledDimension>("SampledDimension");

    class_<RangeDimension>("RangeDimension");

    class_<SetDimension>("SetDimension");

    class_<SimpleTag>("SimpleTag");

    class_<DataTag>("DataTag");

    class_<Feature>("Feature");

    // TODO enum class LinkType

    to_python_converter<std::vector<Section>, vector_transmogrify<Section>>();
    to_python_converter<boost::optional<Section>, option_transmogrify<Section>>();

    to_python_converter<std::vector<Block>, vector_transmogrify<Block>>();

    to_python_converter<std::vector<DataArray>, vector_transmogrify<DataArray>>();

    to_python_converter<boost::optional<std::string>, option_transmogrify<std::string>>();
    option_transmogrify<std::string>::register_from_python();
}
