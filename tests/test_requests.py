import json
import falcon
import responses
import unittest
import falcon.testing as testing

from prom_finagle_exporter.handler import healthHandler, metricHandler
from prom_finagle_exporter.prom import TwitterFinagleCollector


class TestHealthRequest(testing.TestBase):
    def before(self):
        self.api.add_route('/health', healthHandler())
        self.api.add_route('/metrics', metricHandler(
            'http://example.com/metrics.json',
            'api',
            exclude=[]
            ))

    def test_get_health(self):
        body = self.simulate_request('/health', decode='utf-8')
        json_body = json.loads(body)
        self.assertEqual(json_body, {'status': 'OK'})
        self.assertEqual(self.srmock.status, falcon.HTTP_200)

    @responses.activate
    def test_get_metric(self):
        assert_body = [
            '# HELP finigel_jvm_heap finigel_jvm_heap',
            '# TYPE finigel_jvm_heap gauge',
            'finigel_jvm_heap{heap_type="max",original_metric="jvm/heap/max",service="api"} 22212048.0',
            'finigel_jvm_heap{heap_type="committed",original_metric="jvm/heap/committed",service="api"} 22212048.0'
            ]
        url = 'http://example.com/metrics.json'
        responses.add(
            responses.GET,
            url,
            json={
                "jvm/heap/max": 22212048,
                "jvm/heap/committed": 22212048,
                },
            status=200
            )

        resp = self.simulate_request('/metrics', decode='utf-8')
        resp_as_list = [x for x in resp.split('\n') if x]
        self.assertEqual(resp_as_list[-1], assert_body[-1])
        self.assertEqual(resp_as_list[-2], assert_body[-2])
        self.assertEqual(resp_as_list[-3], assert_body[-3])
        self.assertEqual(resp_as_list[-4], assert_body[-4])


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
