#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <fstream>

/*
Written by Junnyung Hur 23-02-19
*/

long long GetFileSize(const char* file_path){
	std::ifstream is(file_path, std::ifstream::binary);
	if (is) {
		is.seekg(0, is.end);
		long long file_size = (long long)is.tellg();
		is.seekg(0, is.beg);
		return file_size;
	}
	return -1;
}

long long ReadFile(const char* file_path, char **_data, long long *remain_size)
{
	long long max_read_size = (long long) 1024*1024*1024;
	std::ifstream is(file_path, std::ifstream::binary);
	if (is) {
		is.seekg(0, is.end);
		long long total_size = (long long)is.tellg();
		long long cur_start_point = total_size - *remain_size;
		is.seekg(cur_start_point, is.beg);

		if(*remain_size >= max_read_size){
			char *buffer = (char*)malloc(max_read_size-1);
			is.read((char*)buffer, max_read_size-1);
			is.close();
			*_data = buffer;
			*remain_size = *remain_size-max_read_size-1;
			return max_read_size-1;
		} else {
			long long target_read_size = *remain_size;
			char * buffer = (char*)malloc(target_read_size);
			is.read((char*)buffer, target_read_size);
			is.close();
			*_data = buffer;
			*remain_size = 0;
			return target_read_size;
		}
	}
	return -1;
}

static PyObject* AEChunking(PyObject *self, PyObject *args)
{
//    std::locale::global(std::locale(".UTF-8"));

    PyObject *file_path_obj, *file_path_bytes;
    char *file_path;
    unsigned int window_size;
    PyObject *ret_list = PyList_New(0);

    if (!PyArg_ParseTuple(args, "OI", &file_path_obj, &window_size))
        return NULL;
    if (file_path_obj != Py_None){
        if (!PyUnicode_FSConverter(file_path_obj, &file_path_bytes))
            return NULL;
        file_path = PyBytes_AsString(file_path_bytes);
    } else {
        return NULL;
    }
    Py_DECREF(file_path_obj);
    Py_DECREF(file_path_bytes);

    char *buffer;
	long long remain_size = GetFileSize(file_path);
	while (remain_size){
		long long read_size = ReadFile(file_path, &buffer, &remain_size);
		long long cursor_pos = 0, current_start_pos = 0, max_pos = 0;
		unsigned char max_value;
		while (cursor_pos < read_size) {
			max_value = buffer[cursor_pos];
			max_pos = cursor_pos;
			while (cursor_pos < read_size) {
			    if (buffer[cursor_pos] <= max_value) {
					if (cursor_pos == max_pos + window_size) {
					    long long chunk_size = cursor_pos - current_start_pos + 1;
					    PyObject *chunk = PyBytes_FromStringAndSize(buffer + current_start_pos, chunk_size);
                        PyList_Append(ret_list, chunk);
                        Py_DECREF(chunk);
						current_start_pos = ++cursor_pos;
						break;
					}
				}
				else {
					max_value = buffer[cursor_pos];
					max_pos = cursor_pos;
				}
				cursor_pos++;
			}
		}
		if (current_start_pos != cursor_pos) {
            long long chunk_size = cursor_pos - current_start_pos;
            PyObject *chunk = PyBytes_FromStringAndSize(buffer + current_start_pos, chunk_size);
            PyList_Append(ret_list, chunk);
            Py_DECREF(chunk);
		}
		free(buffer);
	}

    Py_INCREF(ret_list);
	return ret_list;
}

static PyMethodDef MuseumMethods[]={
    {"ae_chunking" , AEChunking , METH_VARARGS , "Asymmetric Extremum Chunking"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef MuseumModule = {
    PyModuleDef_HEAD_INIT,
    "cext",
    "MUSEUM preprocessing module implemented by C language",
    -1,
    MuseumMethods
};

PyMODINIT_FUNC
PyInit_cext(void)
{
    return PyModule_Create(&MuseumModule);
}
