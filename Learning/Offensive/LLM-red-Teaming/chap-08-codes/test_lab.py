"""Small smoke tests for the deterministic portions of the lab."""
import unittest
from unittest.mock import patch
import app as lab

class LabSmokeTests(unittest.TestCase):
    def setUp(self):
        lab.INVOICES.clear()
        lab.EVENTS.clear()
        self.client=lab.app.test_client()

    def add_invoice(self, customer, service):
        r=self.client.post('/invoice',data={'customer':customer,'service':service,'transform':'literal'})
        self.assertEqual(r.status_code,302)
        return r.headers['Location'].split('/')[-1]

    def test_health(self):
        self.assertEqual(self.client.get('/health').json['status'],'ok')

    def test_xss_unsafe_vs_safe(self):
        inv=self.add_invoice("<img src=x onerror=alert('LAB-XSS')>",'test')
        vulnerable=self.client.get(f'/xss/{inv}/vulnerable').data.decode()
        safe=self.client.get(f'/xss/{inv}/safe').data.decode()
        self.assertIn('<img src=x',vulnerable)
        self.assertIn('&lt;img src=x',safe)

    def test_ssti_arithmetic_vs_safe(self):
        inv=self.add_invoice('Ada','{{ 7 * 7 }}')
        vulnerable=self.client.get(f'/ssti/{inv}/vulnerable').data.decode()
        safe=self.client.get(f'/ssti/{inv}/safe').data.decode()
        self.assertIn('>49</pre>',vulnerable)
        self.assertIn('{{ 7 * 7 }}',safe)

    def test_ssrf_hardened_prevents_internal(self):
        data={'target':'http://internal:8765/metadata','mode':'safe'}
        self.assertIn('BLOCKED:',self.client.post('/fetch',data=data).data.decode())

    def test_ssrf_vulnerable_calls_internal(self):
        with patch.object(lab.requests,'get') as get:
            get.return_value.status_code=200
            get.return_value.text='{"training_only": true}'
            resp=self.client.post('/fetch',data={'target':'http://internal:8765/metadata','mode':'vulnerable'})
            self.assertIn('training_only',resp.data.decode())
            get.assert_called_once()

    def test_command_injection(self):
        data={'host':'127.0.0.1; echo LAB_CMD_OK','mode':'vulnerable'}
        self.assertIn('LAB_CMD_OK',self.client.post('/command',data=data).data.decode())
        data['mode']='safe'
        self.assertIn('BLOCKED:',self.client.post('/command',data=data).data.decode())

    def test_sql_injection(self):
        data={'customer':"' OR 1=1 --",'mode':'vulnerable'}
        self.assertIn('Grace Demo',self.client.post('/sql',data=data).data.decode())
        data['mode']='safe'
        self.assertNotIn('Grace Demo',self.client.post('/sql',data=data).data.decode())

if __name__=='__main__':
    unittest.main(verbosity=2)
