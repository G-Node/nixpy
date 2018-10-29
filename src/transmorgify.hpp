// Copyright (c) 2014, German Neuroinformatics Node (G-Node)
//
// All rights reserved.
//
// Redistribution and use in source and binary forms, with or without
// modification, are permitted under the terms of the BSD License. See
// LICENSE file in the root of the Project.

#ifndef NIXPY_TRANSMORGIFY_H
#define NIXPY_TRANSMORGIFY_H

#include <boost/python.hpp>
#include <boost/python/stl_iterator.hpp>

#include <algorithm>
#include <limits>

namespace nixpy {

// TODO transmorgify time_t;

template<typename T>
struct vector_transmogrify {
    static PyObject* convert(const std::vector<T>& vec) {
        namespace bp = boost::python;

        bp::list l = bp::list();

        for(auto& item : vec) {
            l.append(item);
        }

        return bp::incref(bp::tuple(l).ptr());
    }

    typedef boost::python::converter::rvalue_from_python_stage1_data py_s1_data;
    typedef boost::python::converter::rvalue_from_python_storage<std::vector<T>> py_storage;

    static void register_from_python() {
        boost::python::converter::registry::push_back(is_convertible,
                                                      construct,
                                                      boost::python::type_id<std::vector<T>>());
    }

    static void* is_convertible(PyObject* obj){
        return (PySequence_Check(obj) && PyObject_HasAttrString(obj,"__len__")) ? obj : nullptr;
    }

    static void construct(PyObject* obj, py_s1_data* data) {
        using namespace boost::python;

        void *raw = static_cast<void *>(reinterpret_cast<py_storage *>(data)->storage.bytes);

        int length = PySequence_Size(obj);
        new (raw) std::vector<T>();

        std::vector<T>* vec= static_cast<std::vector<T> *>(raw);

        for(int index = 0; index < length; index++) {
            vec->push_back(extract<T>(PySequence_GetItem(obj, index)));
        }

        data->convertible = raw;
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
        using namespace boost::python;

        bool ok = (obj == Py_None);

        if (!ok) {
            extract<T> extractor(obj);
            ok = extractor.check();
        }

        return ok ? obj : nullptr;
    }

    static void construct(PyObject *obj, py_s1_data *data) {
        using namespace boost::python;

        void *raw = static_cast<void *>(reinterpret_cast<py_storage *>(data)->storage.bytes);

        if (obj == Py_None) {
            new (raw) boost::optional<T>{};
        } else {
            new (raw) boost::optional<T>(extract<T>(obj));
        }
        data->convertible = raw;
    }
};

template<typename U, typename T = long>
PyObject* transmorgify_integer(const U value, const U max_val)
{
    //maybe we should max_val a boost::optional with a default parameter
    //of boost::none, so we can call it with just value
    const bool can_downgrade = max_val < std::numeric_limits<T>::max();
    if (can_downgrade) {
#if PY_MAJOR_VERSION >= 3
        return PyLong_FromLong(static_cast<T>(value));
#else
        return PyInt_FromLong(static_cast<T>(value));
#endif
    } else if (std::numeric_limits<U>::is_signed) {
        return PyLong_FromLongLong(value);
    } else {
        return PyLong_FromUnsignedLongLong(value);
    }
}

struct ndsize_transmogrify {

    typedef nix::NDSize::value_type value_type;

    typedef boost::python::converter::rvalue_from_python_stage1_data py_s1_data;
    typedef boost::python::converter::rvalue_from_python_storage<nix::NDSize> py_storage;

    // nix::NDSize -> PyObject*
    static PyObject* convert(const nix::NDSize& size) {
        namespace bp = boost::python;

        PyObject *tuple = PyTuple_New(size.size());

        auto max_elm = std::max_element(std::begin(size), std::end(size));
        value_type max_val = max_elm != std::end(size) ? *max_elm : 0;

        Py_ssize_t i = 0;
        for (const auto& item : size) {
            PyTuple_SET_ITEM(tuple, i++, transmorgify_integer(item, max_val));
        }

        return tuple;
    }

    // PyObject* -> nix::NDSize
    static void register_from_python() {
        boost::python::converter::registry::push_back(is_convertible,
                                                      construct,
                                                      boost::python::type_id<nix::NDSize>());
    }

    static void* is_convertible(PyObject *obj) {
        namespace bp = boost::python;

        const bp::extract<bp::tuple> extractor(obj);
        return extractor.check() ? obj : nullptr;
    }

    static void construct(PyObject *obj, py_s1_data *data) {
        namespace bp = boost::python;

        void *raw = static_cast<void *>(reinterpret_cast<py_storage *>(data)->storage.bytes);

        const bp::tuple size_py = bp::extract<bp::tuple>(obj);

        ssize_t n_signed = bp::len(size_py);
        if (n_signed < 0) {
            n_signed = 0;
        }
        size_t n = static_cast<size_t>(n_signed);

        nix::NDSize * const size_cc = new (raw) nix::NDSize(n);

        for (size_t i = 0; i < n; i++) {
            (*size_cc)[i] = bp::extract<value_type>(size_py[i]);
        }

        data->convertible = raw;
    }
};

}

#endif // NIXPY_TRANSMORGIFY_H
