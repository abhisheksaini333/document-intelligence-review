import unittest, tempfile, pathlib, json, math, os
from unittest.mock import patch, Mock

class Maintenance(unittest.TestCase):

    def test_dir01(self):
        from docreview.domain import Field,Box
        base=dict(name='total',value='1',confidence=.8,page=1,box=None,method='ocr')
        for name,value in [('page',True),('page',1.5),('confidence',True),('confidence','1'),('box',{}),('method','')]:
            with self.assertRaises(ValueError):Field(**{**base,name:value})
        self.assertEqual(Field(**base).page,1)

    def test_dir02(self):
        from docreview.domain import Token,Box
        base=dict(text='total',confidence=95,box=Box(0,0,1,1),page=1)
        for key,value in [('text',None),('text',7),('box',None),('confidence',True),('confidence','95')]:
            with self.assertRaises(ValueError):Token(**{**base,key:value})
        self.assertEqual(Token(**base).text,'total')

    def test_dir03(self):
        from docreview.normalize import amount
        with self.assertRaises(ValueError):amount('(-1.00)')
        with self.assertRaises(ValueError):amount('9'*200)
        self.assertEqual(amount('(USD 1,000.25)'),'-1000.25')
        self.assertEqual(amount('-1.00'),'-1.00')

    def test_dir04(self):
        from docreview.review import route
        fields={k:{'value':v,'confidence':.99} for k,v in [('number','I'),('date','2022-01-01'),('total','10')]}
        for confidence in (float('nan'),float('inf'),True,2,None):
            result=route({'fields':fields,'prediction':{'confidence':confidence}})
            self.assertEqual(result['recommendation'],'review')
            self.assertIn('invalid_classification',result['reasons'])
        self.assertEqual(route({'fields':fields,'prediction':{'confidence':.99}})['recommendation'],'eligible')

    def test_dir05(self):
        from docreview.extraction import field_issues
        for value in (None,{}, {'value':'NaN'},{'value':'garbage'}):
            self.assertIn('invalid_total',field_issues({'total':value}))
        self.assertEqual(field_issues(None),['invalid_fields'])
        fields={k:{'value':v} for k,v in [('number','I'),('date','2022-01-01'),('subtotal','10'),('tax','2'),('total','13')]}
        self.assertIn('total_mismatch',field_issues(fields));fields['total']['value']='12'
        self.assertEqual(field_issues(fields),[])

    def test_dir06(self):
        from docreview.dataset import audit_split
        row={'id':'a','family':'one','text':'invoice'}
        with self.assertRaisesRegex(ValueError,'Duplicate'):audit_split({'train':[row,dict(row)]})
        self.assertTrue(audit_split({'train':[row,{**row,'id':'b'}]}))
