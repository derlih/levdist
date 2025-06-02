#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include <stdlib.h>
#include <vector>

#define MIN(X, Y) (((X) < (Y)) ? (X) : (Y))

template <typename T> class PyAllocator {
public:
  typedef T value_type;
  // Constructor
  PyAllocator() noexcept {}
  // Allocate memory for n objects of type T
  T *allocate(std::size_t n) { return PyMem_New(T, n); }
  // Deallocate memory
  void deallocate(T *p, std::size_t n) noexcept { PyMem_Del(p); }
};

// clang-format off
// MacOS compiler doesn't like ">>" in template alias
template <typename T> using Vector = std::vector<T, PyAllocator<T> >;
// clang-format on

template <typename CharT>
Py_ssize_t calc_distance(CharT *data_a, Py_ssize_t len_a, CharT *data_b,
                         Py_ssize_t len_b) {
  Vector<Py_ssize_t> v(2 * (len_b + 1));
  Py_ssize_t *v0 = v.data();
  Py_ssize_t *v1 = v0 + len_b + 1;

  for (Py_ssize_t i = 0; i < len_b + 1; ++i) {
    v0[i] = i;
  }

  Py_ssize_t deletion_cost, insertion_cost, substitution_cost;
  for (Py_ssize_t i = 0; i < len_a; ++i) {
    v1[0] = i + 1;

    for (Py_ssize_t j = 0; j < len_b; ++j) {
      deletion_cost = v0[j + 1] + 1;
      insertion_cost = v1[j] + 1;

      if (data_a[i] == data_b[j]) {
        substitution_cost = v0[j];
      } else {
        substitution_cost = v0[j] + 1;
      }

      v1[j + 1] = MIN(MIN(deletion_cost, insertion_cost), substitution_cost);
    }

    std::swap(v0, v1);
  }

  return v0[len_b];
}

static PyObject *method_wagner_fischer(PyObject *self, PyObject *args) {
  PyObject *a;
  PyObject *b;

  if (!PyArg_ParseTuple(args, "UU", &a, &b)) {
    PyErr_SetString(PyExc_TypeError, "Can't parse arguments");
    return NULL;
  }

  const Py_ssize_t len_a = PyUnicode_GetLength(a);
  const Py_ssize_t len_b = PyUnicode_GetLength(b);

  if (len_a == 0) {
    return PyLong_FromSsize_t(len_b);
  }

  if (len_b == 0) {
    return PyLong_FromSsize_t(len_a);
  }

  if (len_a == len_b && PyUnicode_Compare(a, b) == 0) {
    return PyLong_FromSsize_t(0);
  }

  int kind_a = PyUnicode_KIND(a);
  int kind_b = PyUnicode_KIND(b);

  if (kind_a == kind_b) {
    switch (kind_a) {
    case PyUnicode_1BYTE_KIND:
      return PyLong_FromSsize_t(calc_distance(PyUnicode_1BYTE_DATA(a), len_a,
                                              PyUnicode_1BYTE_DATA(b), len_b));
    case PyUnicode_2BYTE_KIND:
      return PyLong_FromSsize_t(calc_distance(PyUnicode_2BYTE_DATA(a), len_a,
                                              PyUnicode_2BYTE_DATA(b), len_b));
    case PyUnicode_4BYTE_KIND:
      return PyLong_FromSsize_t(calc_distance(PyUnicode_4BYTE_DATA(a), len_a,
                                              PyUnicode_4BYTE_DATA(b), len_b));
    }
  }

  void *data_a = PyUnicode_DATA(a);
  Vector<Py_UCS4> converted_a(len_a);
  for (Py_ssize_t i = 0; i < len_a; ++i) {
    converted_a[i] = PyUnicode_READ(kind_a, data_a, i);
  }
  void *data_b = PyUnicode_DATA(b);
  Vector<Py_UCS4> converted_b(len_b);
  for (Py_ssize_t i = 0; i < len_b; ++i) {
    converted_b[i] = PyUnicode_READ(kind_b, data_b, i);
  }
  return PyLong_FromSsize_t(
      calc_distance(converted_a.data(), len_a, converted_b.data(), len_b));
}

static PyMethodDef NativeMethods[] = {
    {"wagner_fischer_native", method_wagner_fischer, METH_VARARGS,
     "Calculate edit distance using a fast (Wagner-Fisher) algorithm.\n"
     "\n"
     "    Args:\n"
     "        a (str): First string\n"
     "        b (str): Second string"
     "\n"
     "    Returns:\n"
     "        int: Edit distance\n"
     "\n"},
    {NULL, NULL, 0, NULL}};

static struct PyModuleDef nativemodule = {PyModuleDef_HEAD_INIT, "native", NULL,
                                          -1, NativeMethods};

PyMODINIT_FUNC PyInit__native(void) { return PyModule_Create(&nativemodule); }
