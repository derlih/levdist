#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include <stdlib.h>
#include <string.h>
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

template <typename CharA, typename CharB>
Py_ssize_t calc_distance(const CharA *data_a, Py_ssize_t len_a,
                         const CharB *data_b, Py_ssize_t len_b) {
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

typedef Py_ssize_t (*DistanceFn)(const void *, Py_ssize_t, const void *,
                                 Py_ssize_t);

template <typename CharA, typename CharB>
static Py_ssize_t typed_distance(const void *a, Py_ssize_t len_a, const void *b,
                                 Py_ssize_t len_b) {
  return calc_distance(static_cast<const CharA *>(a), len_a,
                       static_cast<const CharB *>(b), len_b);
}

constexpr int kind_to_idx(int kind) noexcept {
  switch (kind) {
  case PyUnicode_1BYTE_KIND:
    return 0;
  case PyUnicode_2BYTE_KIND:
    return 1;
  default:
    return 2; // PyUnicode_4BYTE_KIND
  }
}

static constexpr DistanceFn distance_fns[3][3] = {
    {typed_distance<Py_UCS1, Py_UCS1>, typed_distance<Py_UCS1, Py_UCS2>,
     typed_distance<Py_UCS1, Py_UCS4>},
    {typed_distance<Py_UCS2, Py_UCS1>, typed_distance<Py_UCS2, Py_UCS2>,
     typed_distance<Py_UCS2, Py_UCS4>},
    {typed_distance<Py_UCS4, Py_UCS1>, typed_distance<Py_UCS4, Py_UCS2>,
     typed_distance<Py_UCS4, Py_UCS4>},
};

static PyObject *method_wagner_fischer(PyObject *self, PyObject *args) {
  PyObject *a;
  PyObject *b;

  if (!PyArg_ParseTuple(args, "OO", &a, &b)) {
    return NULL;
  }

  const bool a_bytes = PyBytes_Check(a) != 0;
  const bool b_bytes = PyBytes_Check(b) != 0;
  const bool a_str = PyUnicode_Check(a) != 0;
  const bool b_str = PyUnicode_Check(b) != 0;

  if (!a_bytes && !a_str) {
    PyErr_SetString(PyExc_TypeError, "arguments must be str or bytes");
    return NULL;
  }
  if (!b_bytes && !b_str) {
    PyErr_SetString(PyExc_TypeError, "arguments must be str or bytes");
    return NULL;
  }

  const Py_ssize_t len_a =
      a_bytes ? PyBytes_GET_SIZE(a) : PyUnicode_GetLength(a);
  const Py_ssize_t len_b =
      b_bytes ? PyBytes_GET_SIZE(b) : PyUnicode_GetLength(b);

  if (len_a == 0)
    return PyLong_FromSsize_t(len_b);
  if (len_b == 0)
    return PyLong_FromSsize_t(len_a);

  if (len_a == len_b) {
    if (a_str && b_str && PyUnicode_Compare(a, b) == 0)
      return PyLong_FromSsize_t(0);
    if (a_bytes && b_bytes &&
        memcmp(PyBytes_AS_STRING(a), PyBytes_AS_STRING(b), (size_t)len_a) == 0)
      return PyLong_FromSsize_t(0);
  }

  // bytes is equivalent to UCS1: byte values 0–255 equal Latin-1 code points
  int kind_a = a_bytes ? PyUnicode_1BYTE_KIND : PyUnicode_KIND(a);
  int kind_b = b_bytes ? PyUnicode_1BYTE_KIND : PyUnicode_KIND(b);
  const void *ptr_a =
      a_bytes ? (const void *)PyBytes_AS_STRING(a) : PyUnicode_DATA(a);
  const void *ptr_b =
      b_bytes ? (const void *)PyBytes_AS_STRING(b) : PyUnicode_DATA(b);
  Py_ssize_t row_len = len_a, col_len = len_b;

  // Ensure b is the shorter string so the working array is sized to min(len_a,
  // len_b).
  if (row_len < col_len) {
    std::swap(ptr_a, ptr_b);
    std::swap(row_len, col_len);
    std::swap(kind_a, kind_b);
  }

  const auto distance_fn =
      distance_fns[kind_to_idx(kind_a)][kind_to_idx(kind_b)];
  return PyLong_FromSsize_t(distance_fn(ptr_a, row_len, ptr_b, col_len));
}

static PyMethodDef NativeMethods[] = {
    {"wagner_fischer_native", method_wagner_fischer, METH_VARARGS,
     "Calculate edit distance using a fast (Wagner-Fisher) algorithm.\n"
     "\n"
     "    Args:\n"
     "        a (str | bytes): First string\n"
     "        b (str | bytes): Second string"
     "\n"
     "    Returns:\n"
     "        int: Edit distance\n"
     "\n"},
    {NULL, NULL, 0, NULL}};

static struct PyModuleDef nativemodule = {PyModuleDef_HEAD_INIT, "native", NULL,
                                          -1, NativeMethods};

PyMODINIT_FUNC PyInit__native(void) { return PyModule_Create(&nativemodule); }
