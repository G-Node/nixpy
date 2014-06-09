// Copyright (c) 2013, German Neuroinformatics Node (G-Node)
//
// All rights reserved.
//
// Redistribution and use in source and binary forms, with or without
// modification, are permitted under the terms of the BSD License. See
// LICENSE file in the root of the Project.

#ifndef NIXPY_TRANSMORGIFY_H
#define NIXPY_TRANSMORGIFY_H

#include <boost/python.hpp>

namespace nixpy {

// TODO transmorgify time_t;

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

}

#endif // NIXPY_TRANSMORGIFY_H
