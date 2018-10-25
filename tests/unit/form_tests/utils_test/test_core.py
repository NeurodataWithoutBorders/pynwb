import unittest2 as unittest
from six import text_type

from pynwb.form.utils import docval, fmt_docval_args


class MyTestClass(object):

    @docval({'name': 'arg1', 'type': str, 'doc': 'argument1 is a str'})
    def basic_add(self, **kwargs):
        return kwargs

    @docval({'name': 'arg1', 'type': str, 'doc': 'argument1 is a str'},
            {'name': 'arg2', 'type': int, 'doc': 'argument2 is a int'})
    def basic_add2(self, **kwargs):
        return kwargs

    @docval({'name': 'arg1', 'type': text_type, 'doc': 'argument1 is a str'},  # noqa: F40
            {'name': 'arg2', 'type': int, 'doc': 'argument2 is a int'})
    def basic_add2_text_type(self, **kwargs):
        return kwargs

    @docval({'name': 'arg1', 'type': str, 'doc': 'argument1 is a str'},
            {'name': 'arg2', 'type': 'int', 'doc': 'argument2 is a int'},
            {'name': 'arg3', 'type': bool, 'doc': 'argument3 is a bool. it defaults to False', 'default': False})
    def basic_add2_kw(self, **kwargs):
        return kwargs

    @docval({'name': 'arg1', 'type': str, 'doc': 'argument1 is a str', 'default': 'a'},
            {'name': 'arg2', 'type': int, 'doc': 'argument2 is a int', 'default': 1})
    def basic_only_kw(self, **kwargs):
        return kwargs


class MyTestSubclass(MyTestClass):

    @docval({'name': 'arg1', 'type': str, 'doc': 'argument1 is a str'},
            {'name': 'arg2', 'type': int, 'doc': 'argument2 is a int'})
    def basic_add(self, **kwargs):
        return kwargs

    @docval({'name': 'arg1', 'type': str, 'doc': 'argument1 is a str'},
            {'name': 'arg2', 'type': int, 'doc': 'argument2 is a int'},
            {'name': 'arg3', 'type': bool, 'doc': 'argument3 is a bool. it defaults to False', 'default': False},
            {'name': 'arg4', 'type': str, 'doc': 'argument4 is a str'},
            {'name': 'arg5', 'type': 'float', 'doc': 'argument5 is a float'},
            {'name': 'arg6', 'type': bool, 'doc': 'argument6 is a bool. it defaults to False', 'default': None})
    def basic_add2_kw(self, **kwargs):
        return kwargs


class TestDocValidator(unittest.TestCase):

    def setUp(self):
        self.test_obj = MyTestClass()
        self.test_obj_sub = MyTestSubclass()

    def test_bad_type(self):
        exp_msg = "argtype must be a type, a str, a list, a tuple, or None - got <class|type 'dict'>"
        with self.assertRaisesRegex(ValueError, exp_msg):
            @docval({'name': 'arg1', 'type': {'a': 1}, 'doc': 'this is a bad type'})
            def method(self, **kwargs):
                pass
            method(self, arg1=1234560)

    def test_bad_shape(self):
        @docval({'name': 'arg1', 'type': 'array_data', 'doc': 'this is a bad shape', 'shape': (None, 2)})
        def method(self, **kwargs):
            pass
        with self.assertRaises(ValueError):
            method(self, arg1=[[1]])
        with self.assertRaises(ValueError):
            method(self, arg1=[1])
        # this should work
        method(self, arg1=[[1, 1]])

    def test_multi_shape(self):
        @docval({'name': 'arg1', 'type': 'array_data', 'doc': 'this is a bad shape',
                 'shape': ((None,), (None, 2))})
        def method1(self, **kwargs):
            pass

        method1(self, arg1=[[1, 1]])
        method1(self, arg1=[1, 2])
        with self.assertRaises(ValueError):
            method1(self, arg1=[[1, 1, 1]])

    def test_fmt_docval_args(self):
        """ Test that fmt_docval_args works """
        test_kwargs = {
            'arg1': 'a string',
            'arg2': 1,
            'arg3': True,
        }
        rec_args, rec_kwargs = fmt_docval_args(self.test_obj.basic_add2_kw, test_kwargs)
        exp_args = ['a string', 1]
        self.assertListEqual(rec_args, exp_args)
        exp_kwargs = {'arg3': True}
        self.assertDictEqual(rec_kwargs, exp_kwargs)

    def test_docval_add(self):
        """Test that docval works with a single positional
           argument
        """
        kwargs = self.test_obj.basic_add('a string')
        self.assertDictEqual(kwargs, {'arg1': 'a string'})

    def test_docval_add_kw(self):
        """Test that docval works with a single positional
           argument passed as key-value
        """
        kwargs = self.test_obj.basic_add(arg1='a string')
        self.assertDictEqual(kwargs, {'arg1': 'a string'})

    def test_docval_add_missing_args(self):
        """Test that docval catches missing argument
           with a single positional argument
        """
        with self.assertRaises(TypeError) as cm:
            kwargs = self.test_obj.basic_add()  # noqa: F841
        msg = "missing argument 'arg1'"
        self.assertEqual(cm.exception.args[0], msg)

    def test_docval_add2(self):
        """Test that docval works with two positional
           arguments
        """
        kwargs = self.test_obj.basic_add2('a string', 100)
        self.assertDictEqual(kwargs, {'arg1': 'a string', 'arg2': 100})

    def test_docval_add2_text_type_w_str(self):
        """Test that docval works with two positional
           arguments
        """
        kwargs = self.test_obj.basic_add2_text_type('a string', 100)
        self.assertDictEqual(kwargs, {'arg1': 'a string', 'arg2': 100})

    def test_docval_add2_text_type_w_unicode(self):
        """Test that docval works with two positional
           arguments
        """
        kwargs = self.test_obj.basic_add2_text_type(u'a string', 100)
        self.assertDictEqual(kwargs, {'arg1': u'a string', 'arg2': 100})

    def test_docval_add2_kw_default(self):
        """Test that docval works with two positional
           arguments and a keyword argument when using
           default keyword argument value
        """
        kwargs = self.test_obj.basic_add2_kw('a string', 100)
        self.assertDictEqual(kwargs, {'arg1': 'a string', 'arg2': 100, 'arg3': False})

    def test_docval_add2_pos_as_kw(self):
        """Test that docval works with two positional
           arguments and a keyword argument when using
           default keyword argument value, but pass
           positional arguments by key-value
        """
        kwargs = self.test_obj.basic_add2_kw(arg1='a string', arg2=100)
        self.assertDictEqual(kwargs, {'arg1': 'a string', 'arg2': 100, 'arg3': False})

    def test_docval_add2_kw_kw_syntax(self):
        """Test that docval works with two positional
           arguments and a keyword argument when specifying
           keyword argument value with keyword syntax
        """
        kwargs = self.test_obj.basic_add2_kw('a string', 100, arg3=True)
        self.assertDictEqual(kwargs, {'arg1': 'a string', 'arg2': 100, 'arg3': True})

    def test_docval_add2_kw_all_kw_syntax(self):
        """Test that docval works with two positional
           arguments and a keyword argument when specifying
           all arguments by key-value
        """
        kwargs = self.test_obj.basic_add2_kw(arg1='a string', arg2=100, arg3=True)
        self.assertDictEqual(kwargs, {'arg1': 'a string', 'arg2': 100, 'arg3': True})

    def test_docval_add2_kw_pos_syntax(self):
        """Test that docval works with two positional
           arguments and a keyword argument when specifying
           keyword argument value with positional syntax
        """
        kwargs = self.test_obj.basic_add2_kw('a string', 100, True)
        self.assertDictEqual(kwargs, {'arg1': 'a string', 'arg2': 100, 'arg3': True})

    def test_docval_add2_kw_pos_syntax_missing_args(self):
        """Test that docval catches incorrect type with two positional
           arguments and a keyword argument when specifying
           keyword argument value with positional syntax
        """
        with self.assertRaises(TypeError) as cm:
            kwargs = self.test_obj.basic_add2_kw('a string', 'bad string')  # noqa: F841

        self.assertEqual(cm.exception.args[0], u"incorrect type for 'arg2' (got 'str', expected 'int')")

    def test_docval_add_sub(self):
        """Test that docval works with a two positional arguments,
           where the second is specified by the subclass implementation
        """
        kwargs = self.test_obj_sub.basic_add('a string', 100)
        expected = {'arg1': 'a string', 'arg2': 100}
        self.assertDictEqual(kwargs, expected)

    def test_docval_add2_kw_default_sub(self):
        """Test that docval works with a four positional arguments and
           two keyword arguments, where two positional and one keyword
           argument is specified in both the parent and sublcass implementations
        """
        kwargs = self.test_obj_sub.basic_add2_kw('a string', 100, 'another string', 200.0)
        expected = {'arg1': 'a string', 'arg2': 100,
                    'arg4': 'another string', 'arg5': 200.0,
                    'arg3': False, 'arg6': None}
        self.assertDictEqual(kwargs, expected)

    def test_docval_add2_kw_default_sub_missing_args(self):
        """Test that docval catches missing arguments with a four positional arguments
           and two keyword arguments, where two positional and one keyword
           argument is specified in both the parent and sublcass implementations,
           when using default values for keyword arguments
        """
        with self.assertRaises(TypeError) as cm:
            kwargs = self.test_obj_sub.basic_add2_kw('a string', 100, 'another string')  # noqa: F841
        msg = "missing argument 'arg5'"
        self.assertEqual(cm.exception.args[0], msg)

    def test_docval_add2_kw_kwsyntax_sub(self):
        """Test that docval works when called with a four positional
           arguments and two keyword arguments, where two positional
           and one keyword argument is specified in both the parent
           and sublcass implementations
        """
        kwargs = self.test_obj_sub.basic_add2_kw('a string', 100, 'another string', 200.0, arg6=True)
        expected = {'arg1': 'a string', 'arg2': 100,
                    'arg4': 'another string', 'arg5': 200.0,
                    'arg3': False, 'arg6': True}
        self.assertDictEqual(kwargs, expected)

    def test_docval_add2_kw_kwsyntax_sub_missing_args(self):
        """Test that docval catches missing arguments when called with a four positional
           arguments and two keyword arguments, where two positional and one keyword
           argument is specified in both the parent and sublcass implementations
        """
        with self.assertRaises(TypeError) as cm:
            kwargs = self.test_obj_sub.basic_add2_kw('a string', 100, 'another string', arg6=True)  # noqa: F841
        msg = "missing argument 'arg5'"
        self.assertEqual(cm.exception.args[0], msg)

    def test_docval_add2_kw_kwsyntax_sub_nonetype_arg(self):
        """Test that docval catches NoneType  when called with a four positional
           arguments and two keyword arguments, where two positional and one keyword
           argument is specified in both the parent and sublcass implementations
        """
        with self.assertRaises(TypeError) as cm:
            kwargs = self.test_obj_sub.basic_add2_kw('a string', 100, 'another string', None, arg6=True)  # noqa: F841
        msg = "incorrect type for 'arg5' (got 'NoneType', expected 'float')"
        self.assertEqual(cm.exception.args[0], msg)

    def test_only_kw_no_args(self):
        """Test that docval parses arguments when only keyword
           arguments exist, and no arguments are specified
        """
        kwargs = self.test_obj.basic_only_kw()
        self.assertDictEqual(kwargs, {'arg1': 'a', 'arg2': 1})

    def test_only_kw_arg1_no_arg2(self):
        """Test that docval parses arguments when only keyword
           arguments exist, and only first argument is specified
           as key-value
        """
        kwargs = self.test_obj.basic_only_kw(arg1='b')
        self.assertDictEqual(kwargs, {'arg1': 'b', 'arg2': 1})

    def test_only_kw_arg1_pos_no_arg2(self):
        """Test that docval parses arguments when only keyword
           arguments exist, and only first argument is specified
           as positional argument
        """
        kwargs = self.test_obj.basic_only_kw('b')
        self.assertDictEqual(kwargs, {'arg1': 'b', 'arg2': 1})

    def test_only_kw_arg2_no_arg1(self):
        """Test that docval parses arguments when only keyword
           arguments exist, and only second argument is specified
           as key-value
        """
        kwargs = self.test_obj.basic_only_kw(arg2=2)
        self.assertDictEqual(kwargs, {'arg1': 'a', 'arg2': 2})

    def test_only_kw_arg1_arg2(self):
        """Test that docval parses arguments when only keyword
           arguments exist, and both arguments are specified
           as key-value
        """
        kwargs = self.test_obj.basic_only_kw(arg1='b', arg2=2)
        self.assertDictEqual(kwargs, {'arg1': 'b', 'arg2': 2})

    def test_only_kw_arg1_arg2_pos(self):
        """Test that docval parses arguments when only keyword
           arguments exist, and both arguments are specified
           as positional arguments
        """
        kwargs = self.test_obj.basic_only_kw('b', 2)
        self.assertDictEqual(kwargs, {'arg1': 'b', 'arg2': 2})

    def test_extra_kwarg(self):
        """Test that docval parses arguments when only keyword
           arguments exist, and both arguments are specified
           as positional arguments
        """
        with self.assertRaises(TypeError):
            self.test_obj.basic_add2_kw('a string', 100, bar=1000)


if __name__ == '__main__':
    unittest.main()
