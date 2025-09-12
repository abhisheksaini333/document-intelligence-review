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

    def test_dir07(self):
        from docreview.dataset import split
        rows=[{'id':f'{label}-{i}','label':label,'family':f'family-{i}','text':label} for label in ('invoice','receipt') for i in range(5)]
        with self.assertRaisesRegex(ValueError,'family'):split(rows)

    def test_dir08(self):
        from docreview.feedback import merge_training_feedback
        held=[{'id':'held','family':'held-family','text':'held text'}]
        base={'id':'training','family':'training-family','text':'fresh','label':'invoice'}
        for row in ({**base,'id':'held'},{**base,'family':'held-family'},{**base,'text':' HELD  TEXT '}):
            with self.assertRaisesRegex(ValueError,'Training overlaps'):merge_training_feedback([row],[],held)
        self.assertEqual(merge_training_feedback([base],[],held),[base])

    def test_dir09(self):
        from docreview.feedback import merge_training_feedback
        row={'id':'new','family':'new-family','text':'fresh','label':'invoice'}
        with self.assertRaisesRegex(ValueError,'Conflicting'):merge_training_feedback([],[row,{**row,'label':'receipt'}],[])
        self.assertEqual(merge_training_feedback([],[row,dict(row)],[]),[row])

    def test_dir10(self):
        from docreview.metrics import coverage_curve
        for confidence in (float('nan'),float('inf'),True,-1,2,'1'):
            with self.assertRaises(ValueError):coverage_curve(['invoice'],[{'label':'invoice','confidence':confidence}])
        self.assertEqual(coverage_curve(['invoice'],[{'label':'invoice','confidence':1}],[1])[0]['coverage'],1)

    def test_dir11(self):
        from docreview.metrics import calibration
        from docreview.calibration import choose_temperature,temperature_scale
        for bins in (True,1.5,None):
            with self.assertRaises(ValueError):calibration(['a'],[{'a':1}],bins=bins)
        for temperature in (True,None,'1'):
            with self.assertRaises(ValueError):temperature_scale({'a':1},temperature)
        with self.assertRaisesRegex(ValueError,'candidates'):choose_temperature(['a'],[{'a':1}],candidates=[])

    def test_dir12(self):
        from docreview.store import Store,Conflict
        with tempfile.TemporaryDirectory() as d:
            store=Store(pathlib.Path(d)/'db');row=store.create('a'*64,'x','x');claimed=store.claim('worker',now=100)
            reviewed=store.result(row['id'],claimed['version'],{'fields':{}})
            with self.assertRaises(Conflict):store.fail(row['id'],reviewed['version'],'late failure')
            self.assertEqual(store.get(row['id'])['status'],'review')
            fresh=store.create('b'*64,'y','y')
            with self.assertRaises(Conflict):store.fail(fresh['id'],fresh['version'],'no lease')

    def test_dir13(self):
        from docreview.store import Store
        with tempfile.TemporaryDirectory() as d:
            store=Store(pathlib.Path(d)/'db');row=store.create('a'*64,'x','x')
            for options in ({'now':float('nan')},{'now':True},{'lease_seconds':True},{'lease_seconds':float('inf')}):
                with self.assertRaises(ValueError):store.claim('worker',**options)
            for worker in (7,' ','worker\n'):
                with self.assertRaises(ValueError):store.claim(worker)
            self.assertEqual(store.get(row['id'])['status'],'queued')
