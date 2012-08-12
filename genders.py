#!/usr/bin/env python26

import ctypes
from ctypes import CDLL, c_char_p, pointer, byref
from ctypes.util import find_library
from ctypes import *

import sys

genders_library_file = find_library('genders')

if not genders_library_file:
    raise NotImplementedError, 'Unable to find genders library'

libgenders = CDLL(genders_library_file)

# Argument types
libgenders.genders_load_data.argtypes = [c_void_p, c_char_p]
libgenders.genders_isnode.argtypes = [c_void_p, c_char_p]
libgenders.genders_isattr.argtypes = [c_void_p, c_char_p]
libgenders.genders_isattrval.argtypes = [c_void_p, c_char_p]

# Non-int return types
libgenders.genders_handle_create.restype = c_void_p
libgenders.genders_strerror.restype = c_char_p
libgenders.genders_errormsg.restype = c_char_p

libgenders.genders_isattr.restype = c_bool
libgenders.genders_isnode.restype = c_bool
libgenders.genders_isattrval.restype = c_bool

libgenders.genders_perror.restype = None

def raise_exception(result, func, args):
    handle = args[0]
    errnum = libgenders.genders_errnum(handle)
    errmsg = libgenders.genders_errormsg(handle)
    errmsg += " from func " + func.__name__
    raise errnum_exceptions[errnum](errmsg)

def errcheck_ltz(result, func, args):
    """ errcheck for functions that return less-than-zero on error """
    if result < 0:
        raise_exception(result, func, args)
    return args

def errcheck_null(result, func, args):
    """ errcheck for functions that return NULL (None) on error """
    if not result:
        raise_exception(result, func, args)
    return args

libgenders.genders_load_data.errcheck = errcheck_ltz


# Exceptions {{{
errnum_exceptions = [None]

# These are ordered so that each index corresponds with the errnum
class ErrNullHandle(Exception): pass
errnum_exceptions.append(ErrNullHandle)

class ErrOpen(Exception): pass
errnum_exceptions.append(ErrOpen)

class ErrRead(Exception): pass
errnum_exceptions.append(ErrRead)

class ErrParse(Exception): pass
errnum_exceptions.append(ErrParse)

class ErrNotLoaded(Exception): pass
errnum_exceptions.append(ErrNotLoaded)

class ErrIsLoaded(Exception): pass
errnum_exceptions.append(ErrIsLoaded)

class ErrOverflow(Exception): pass
errnum_exceptions.append(ErrOverflow)

class ErrParameters(Exception): pass
errnum_exceptions.append(ErrParameters)

class ErrNullPtr(Exception): pass
errnum_exceptions.append(ErrNullPtr)

class ErrNotFound(Exception): pass
errnum_exceptions.append(ErrNotFound)

class ErrOutMem(Exception): pass
errnum_exceptions.append(ErrOutMem)

class ErrSyntax(Exception): pass
errnum_exceptions.append(ErrSyntax)

class ErrMagic(Exception): pass
errnum_exceptions.append(ErrMagic)

class ErrInternal(Exception): pass
errnum_exceptions.append(ErrInternal)

class ErrNumrange(Exception): pass
errnum_exceptions.append(ErrNumrange)

# }}} End Exceptions

class Genders(object):
    def __init__(self, genders_file=None, no_auto=False):

        if not no_auto:
            self.handle_create()
            self.load_data(genders_file)

    def handle_create(self):
        self._handle = libgenders.genders_handle_create()

        if not self._handle:
            raise Exception("Error allocating memory")

    def handle_destroy(self):
        if libgenders.genders_handle_destroy(self._handle) != 0:
            raise errnum_exceptions[self.errnum()]()

    def load_data(self, genders_file=None):
        libgenders.genders_load_data(self._handle, genders_file)

    def errnum(self):
        return libgenders.genders_errnum(self._handle)

    def strerror(self, err):
        return libgenders.genders_strerror(err)

    def errormsg(self):
        return libgenders.genders_errormsg(self._handle)

    def perror(self, msg=None):
        libgenders.genders_perror(self._handle, msg)

    def getnumnodes(self):
        return libgenders.genders_getnumnodes(self._handle)

    def getnumattrs(self):
        return libgenders.genders_getnumattrs(self._handle)

    def getmaxattrs(self):
        return libgenders.genders_getmaxattrs(self._handle)

    def getmaxnodelen(self):
        return libgenders.genders_getmaxnodelen(self._handle)

    def getmaxattrlen(self):
        return libgenders.genders_getmaxattrlen(self._handle)

    def getmaxvallen(self):
        return libgenders.genders_getmaxvallen(self._handle)

    def nodelist_create(self):
        node_list = pointer(c_char_p(1))
        libgenders.genders_nodelist_create(self._handle, byref(node_list))
        return node_list

    def nodelist_clear(self, node_list):
        r = libgenders.genders_nodelist_clear(self._handle, node_list)
        if r < 0:
            raise errnum_exceptions[self.errnum()]

    def nodelist_destroy(self, node_list):
        r = libgenders.genders_nodelist_destroy(self._handle, node_list)
        if r < 0:
            raise errnum_exceptions[self.errnum()]

    # def attrlist_create
    # def attrlist_clear
    # def attrlist_destroy

    # def vallist_create
    # def vallist_clear
    # def vallist_destroy

    # def getnodename

    def getnodes(self, attr=None, val=None, node_list=None):
        if not node_list:
            node_list = self.nodelist_create()
            node_list_destroy = True
        else:
            node_list_destroy = False

        ret = libgenders.genders_getnodes(self._handle, node_list, self.getnumnodes(), attr, val)

        if ret < 0:
            raise errnum_exceptions[self.errnum()]()

        pylist = node_list[0:ret]
        if node_list_destroy:
            self.nodelist_destroy(node_list)
        return pylist

    # def getattr
    # def getattr_all
    # def testattr
    # def testattrval

    def isnode(self, node=None):
        return libgenders.genders_isnode(self._handle, node)

    def isattr(self, attr=None):
        return libgenders.genders_isattr(self._handle, attr)

    def isattrval(self, attr=None, val=None):
        return libgenders.genders_isattrval(self._handle, attr, val)

    # def index_attrvals

    def query(self, query_str):
        node_list = self.nodelist_create()
        query_ret = libgenders.genders_query(self._handle, node_list, self.getnumnodes(), query_str)

        if query_ret < 0:
            raise errnum_exceptions[self.errnum()]()

        pylist = node_list[0:query_ret]
        self.nodelist_destroy(node_list)
        return pylist

    # def testquery
    # def parse

# vim:fdm=marker
