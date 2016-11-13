
from context import pynwb
import unittest


from pynwb.utils import *


class MyTestClass(object):

    @docval({'name': 'arg1', 'type': str, 'doc': 'argument1 is a str'})
    def basic_add(self, **kwargs):
        return kwargs

    @docval({'name': 'arg1', 'type': str, 'doc': 'argument1 is a str'},
            {'name': 'arg2', 'type': int, 'doc': 'argument2 is a int'})
    def basic_add2(self, **kwargs):
        return kwargs
    
    @docval({'name': 'arg1', 'type': str, 'doc': 'argument1 is a str'},
            {'name': 'arg2', 'type': int, 'doc': 'argument2 is a int'},
            {'name': 'arg3', 'type': bool, 'doc': 'argument3 is a bool. it defaults to False', 'default': False})
    def basic_add2_kw(self, **kwargs):
        return kwargs

class MyTestSubclass(MyTestClass):

    @docval(*MyTestClass.basic_add2_kw.docval['args'],
            {'name': 'arg4', 'type': str, 'doc': 'argument4 is a str'},
            {'name': 'arg5', 'type': int, 'doc': 'argument5 is a int'},
            {'name': 'arg6', 'type': bool, 'doc': 'argument6 is a bool. it defaults to False', 'default': False},
            inherit_args=True)
    def basic_add2_kw(self, **kwargs):
        return kwargs

class TestDocValidator(unittest.TestCase):
    
    def setUp(self):
        self.test_obj = MyTestClass()
        self.test_obj_sub = MyTestSubclass()
    
    def test_docval_add(self):
        kwargs = self.test_obj.basic_add('a string')
        self.assertDictEqual(kwargs, {'arg1': 'a string'})
        
    def test_docval_add2(self):
        kwargs = self.test_obj.basic_add2('a string', 100)
        self.assertDictEqual(kwargs, {'arg1': 'a string', 'arg2': 100})
        
    def test_docval_add2_kw_default(self):
        kwargs = self.test_obj.basic_add2_kw('a string', 100)
        self.assertDictEqual(kwargs, {'arg1': 'a string', 'arg2': 100, 'arg3': False})
        
    def test_docval_add2_kw_kwsyntax(self):
        kwargs = self.test_obj.basic_add2_kw('a string', 100, arg3=True)
        self.assertDictEqual(kwargs, {'arg1': 'a string', 'arg2': 100, 'arg3': True})
        
    def test_docval_add2_kw_possyntax(self):
        kwargs = self.test_obj.basic_add2_kw('a string', 100, True)
        self.assertDictEqual(kwargs, {'arg1': 'a string', 'arg2': 100, 'arg3': True})

    def test_docval_add2_kw_default_sub(self):
        kwargs = self.test_obj_sub.basic_add2_kw('a string', 100, 'another string', 200)
        expected = {'arg1': 'a string', 'arg2': 100, 
                    'arg4': 'another string', 'arg5': 200, 
                    'arg3': False, 'arg6': False}
        self.assertDictEqual(kwargs, expected)

    def test_docval_add2_kw_kwsyntax_sub(self):
        kwargs = self.test_obj_sub.basic_add2_kw('a string', 100, 'another string', 200, arg6=True)
        expected = {'arg1': 'a string', 'arg2': 100, 
                    'arg4': 'another string', 'arg5': 200, 
                    'arg3': False, 'arg6': True}
        self.assertDictEqual(kwargs, expected)
