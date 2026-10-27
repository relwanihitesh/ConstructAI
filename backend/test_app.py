import io
import json
import os
import tempfile
import unittest
from unittest.mock import patch

TEMP=tempfile.TemporaryDirectory(dir=os.getcwd(),prefix='.test-')
os.environ['CONSTRUCT_DATA_DIR']=TEMP.name
os.environ['GROQ_API_KEY']=''
os.environ['POLLINATIONS_API_KEY']=''
from fastapi.testclient import TestClient
from PIL import Image
import main

class AppTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.client=TestClient(main.app)

    def image(self):
        b=io.BytesIO();Image.new('RGB',(32,32),'white').save(b,'PNG');return b.getvalue()

    def test_health(self):
        self.assertEqual(self.client.get('/api/health').json()['mode'],'demo')

    def test_planner_math(self):
        r=self.client.post('/api/project-planner',json=dict(location='Pune',area=1000,floors=2,rate=2000))
        self.assertEqual(r.status_code,200)
        data=r.json();self.assertEqual(data['mode'],'demo')
        self.assertEqual(data['metrics'][3]['value'],'INR 4,400,000')
        main.Report.model_validate(data)

    def test_valuation_yield(self):
        r=self.client.post('/api/real-estate-valuation',json=dict(location='Pune',area=1000,rate=5000,building_age=10,monthly_rent=20000))
        self.assertEqual(r.status_code,200)
        self.assertEqual(r.json()['metrics'][3]['value'],'4.80%')

    def test_invalid_numbers(self):
        for field,value in [('area',0),('area',-1),('floors',1.5),('rate',-200)]:
            payload=dict(location='Pune',area=1000,floors=2,rate=2000);payload[field]=value
            self.assertEqual(self.client.post('/api/project-planner',json=payload).status_code,422)

    def test_all_text_modules(self):
        for feature,data in [('site-assistant',dict(activity='Masonry',labour_count=4,site_condition='Dry site')),('weather-advisor',dict(activity='Masonry',weather='Heavy rain')),('chatbot',dict(query='How do I prepare a checklist?')),('knowledge-base',dict(topic='Slab inspection',document_type='Inspection checklist'))]:
            with self.subTest(feature=feature):
                r=self.client.post('/api/'+feature,json=data)
                self.assertEqual(r.status_code,200);main.Report.model_validate(r.json())

    def test_blank_input(self):
        self.assertEqual(self.client.post('/api/chatbot',json={'query':'    '}).status_code,422)

    def test_missing_image(self):
        self.assertEqual(self.client.post('/api/crack-detection',data={'text':'test'}).status_code,422)

    def test_valid_images_not_falsely_assessed(self):
        for path in ('safety-monitor','crack-detection'):
            r=self.client.post('/api/'+path,files={'image':('test.png',self.image(),'image/png')},data={'text':'Inspection'})
            self.assertEqual(r.status_code,200)
            self.assertEqual(r.json()['status'],'Not assessed')

    def test_corrupt_image(self):
        r=self.client.post('/api/safety-monitor',files={'image':('x.jpg',b'not-an-image','image/jpeg')})
        self.assertEqual(r.status_code,422)

    def test_large_upload(self):
        r=self.client.post('/api/safety-monitor',files={'image':('x.jpg',b'x'*(5*1024*1024+1),'image/jpeg')})
        self.assertEqual(r.status_code,413)

    def test_history_and_delete(self):
        r=self.client.post('/api/chatbot',json={'query':'History test'}).json()
        self.assertTrue(any(x['id']==r['id'] for x in self.client.get('/api/history').json()))
        self.assertEqual(self.client.delete('/api/history/'+r['id']).status_code,200)
        self.assertEqual(self.client.delete('/api/history/'+r['id']).status_code,404)

    def test_image_key_required(self):
        self.assertEqual(self.client.post('/api/visualization',json={'prompt':'Modern residential building'}).status_code,503)

    def test_public_visitors_have_separate_history(self):
        with patch.dict(os.environ, {'PUBLIC_DEMO': '1'}):
            first=TestClient(main.app)
            second=TestClient(main.app)
            r=first.post('/api/chatbot',json={'query':'Private visitor worksheet'}).json()
            self.assertTrue(any(item['id']==r['id'] for item in first.get('/api/history').json()))
            self.assertFalse(any(item['id']==r['id'] for item in second.get('/api/history').json()))
            self.assertEqual(second.delete('/api/history/'+r['id']).status_code,404)
            self.assertEqual(first.delete('/api/history/'+r['id']).status_code,200)

    def fake_client(self,content,status=200):
        class Client:
            async def __aenter__(self): return self
            async def __aexit__(self,*args): pass
            async def post(self,*args,**kwargs):
                self.payload=kwargs['json']
                import httpx
                return httpx.Response(status,json={'choices':[{'message':{'content':content}}]})
        return Client()

    def test_ai_success_contract(self):
        output=main.demo('chatbot',{'query':'test'}).model_dump_json()
        fake=self.fake_client(output)
        with patch.dict(os.environ,{'GROQ_API_KEY':'test-key'}), patch('main.httpx.AsyncClient',return_value=fake):
            r=self.client.post('/api/chatbot',json={'query':'test','history':[{'role':'user','content':'Earlier context'}]})
        self.assertEqual(r.status_code,200);self.assertEqual(r.json()['mode'],'ai')
        self.assertIn('Earlier context',fake.payload['messages'][1]['content'][0]['text'])

    def test_ai_malformed_does_not_fabricate(self):
        with patch.dict(os.environ,{'GROQ_API_KEY':'test-key'}), patch('main.httpx.AsyncClient',return_value=self.fake_client('{"title":"bad"}')):
            r=self.client.post('/api/chatbot',json={'query':'test'})
        self.assertEqual(r.status_code,502)

    def test_ai_provider_error(self):
        with patch.dict(os.environ,{'GROQ_API_KEY':'test-key'}), patch('main.httpx.AsyncClient',return_value=self.fake_client('',429)):
            r=self.client.post('/api/chatbot',json={'query':'test'})
        self.assertEqual(r.status_code,502)
        self.assertIn('429',r.json()['detail'])

    def test_image_sent_as_jpeg(self):
        output=main.demo('safety-monitor',{'text':'test'}).model_dump_json()
        fake=self.fake_client(output)
        with patch.dict(os.environ,{'GROQ_API_KEY':'test-key'}), patch('main.httpx.AsyncClient',return_value=fake):
            r=self.client.post('/api/safety-monitor',files={'image':('test.png',self.image(),'image/png')})
        self.assertEqual(r.status_code,200)
        self.assertTrue(fake.payload['messages'][1]['content'][1]['image_url']['url'].startswith('data:image/jpeg;base64,'))

if __name__=='__main__': unittest.main(verbosity=2)
