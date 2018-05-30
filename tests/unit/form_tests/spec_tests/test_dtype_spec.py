import unittest2 as unittest

from pynwb.form.spec import DtypeSpec, DtypeHelper, RefSpec


class DtypeSpecHelper(unittest.TestCase):
    def setUp(self):
        pass

    def test_recommended_dtypes(self):
        self.assertListEqual(DtypeHelper.recommended_primary_dtypes,
                             list(DtypeHelper.primary_dtype_synonyms.keys()))

    def test_valid_primary_dtypes(self):
        a = set(list(DtypeHelper.primary_dtype_synonyms.keys()) +
                [vi for v in DtypeHelper.primary_dtype_synonyms.values() for vi in v])
        self.assertSetEqual(a, DtypeHelper.valid_primary_dtypes)

    def test_simplify_cpd_type(self):
        compound_type = [DtypeSpec('test', 'test field', 'float'),
                         DtypeSpec('test2', 'test field2', 'int')]
        expected_result = ['float', 'int']
        result = DtypeHelper.simplify_cpd_type(compound_type)
        self.assertListEqual(result, expected_result)


class DtypeSpecTests(unittest.TestCase):
    def setUp(self):
        pass

    def test_constructor(self):
        spec = DtypeSpec('column1', 'an example column', 'int')
        self.assertEqual(spec.doc, 'an example column')
        self.assertEqual(spec.name, 'column1')
        self.assertEqual(spec.dtype, 'int')

    def test_build_spec(self):
        spec = DtypeSpec.build_spec({'doc': 'an example column', 'name': 'column1', 'dtype': 'int'})
        self.assertEqual(spec.doc, 'an example column')
        self.assertEqual(spec.name, 'column1')
        self.assertEqual(spec.dtype, 'int')

    def test_invalid_refspec_dict(self):
        with self.assertRaises(AssertionError):
            DtypeSpec.assertValidDtype({'no target': 'test',   # <-- missing or here bad target key for RefSpec
                                        'reftype': 'object'})

    def test_refspec_dtype(self):
        # just making sure this does not cause an error
        DtypeSpec('column1', 'an example column', RefSpec('TimeSeries', 'object'))

    def test_invalid_dtype(self):
        with self.assertRaises(AssertionError):
            DtypeSpec('column1', 'an example column',
                      dtype='bad dtype'                     # <-- make sure a bad type string raises an error
                      )

    def test_is_ref(self):
        spec = DtypeSpec('column1', 'an example column', RefSpec('TimeSeries', 'object'))
        self.assertTrue(DtypeSpec.is_ref(spec))
        spec = DtypeSpec('column1', 'an example column', 'int')
        self.assertFalse(DtypeSpec.is_ref(spec))
