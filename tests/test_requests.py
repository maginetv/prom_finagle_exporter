import json
import falcon
import responses
import unittest
import falcon.testing as testing

from prom_finagle_exporter.handler import healthHandler
from prom_finagle_exporter.prom import TwitterFinagleCollector


class TestHealthRequest(testing.TestBase):
    def before(self):
        self.api.add_route('/health', healthHandler())

    def test_get_health(self):
        body = self.simulate_request('/health', decode='utf-8')
        json_body = json.loads(body)
        self.assertEqual(json_body, {'status': 'OK'})
        self.assertEqual(self.srmock.status, falcon.HTTP_200)


class TestCollectRequest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.url = 'http://localhost:9161/metrics'
        cls.service = 'name_of_service'
        cls.exclude_list = ['finagle_exporter_http_response_ko']

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @responses.activate
    def test_collect_req_correct_data(self):
        url = 'http://example.com/metrics.json'
        service = 'foo'
        collector = TwitterFinagleCollector(url, service)
        responses.add(responses.GET, url, json={"srv/foobar": 22212048}, status=200)

        resp = collector._get_metrics()
        self.assertEqual(resp, {"srv/foobar": 22212048})

    @responses.activate
    def test_collect_req_500(self):
        url = 'http://example.com/metrics.json'
        service = 'foo'
        collector = TwitterFinagleCollector(url, service)
        responses.add(responses.GET, url, status=500)

        resp = collector._get_metrics()
        self.assertFalse(resp)
        self.assertIsInstance(resp, dict)
